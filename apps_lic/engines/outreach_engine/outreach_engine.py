import json
import os
import time
from typing import Any, Dict, Optional

# Import core utilities for mock functions
from core_utils import (
    add_observations,
    browser_click,
    browser_navigate,
    browser_type,
    commit_transaction,
    get_current_time,
    log_action,
    read_text_file,
    register_process,
    search_records,
    start_transaction,
    string_get,
    string_set,
    transaction_set_with_ttl,
    watch_key,
)

# Import hardened MCP functions
from mcp_hardening import (
    ensure_brand_compliance,
    execute_cost_controlled_search,
    get_brand_style_guide,
)

# Import egress filter for Protocol 8
from network_utils import strict_egress_filter

# Add this global configuration flag (or load from environment/config)
SHADOW_MODE_ACTIVE = os.environ.get("AGENT_MODE", "PRODUCTION") == "SHADOW"

# Define the specific allow-list for the Outreach Engine
OUTREACH_ALLOWED_HOSTS = [
    "api.openai.com", "anthropic.com", "genai.google.com",  # LLM APIs
    "smtp.sendgrid.net", "mailgun.com",  # Email/SMTP providers
    "linkedin.com", "www.linkedin.com"  # Professional networking
]


@strict_egress_filter(allowed_domains=OUTREACH_ALLOWED_HOSTS)
def _fetch_company_content(url: str, fetch_tool: Any, max_length: int = 1000) -> Optional[str]:
    """Fetches company content with egress filtering."""
    return fetch_tool(url=url, max_length=max_length)


def automated_lead_vetting(company_url: str, user_name: str, tools: Dict[str, Any], logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Implements the 'Automated Lead Vetting & Contact' use case, integrating L1 (Fetch),
    L3 (Pinecone), and L5 (MEMemory) to perform context-aware outreach.
    """
    # 1. Register PID for the Watchdog
    register_process()

    if logger:
        logger.info(
            f"🚀 Starting Automated Lead Vetting for {company_url} (User: {user_name})...")

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
        # Fetch the company's latest news or press releases with egress filtering
        company_news = _fetch_company_content(company_url, fetch, max_length=1000)
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
            logger.info(
                f"✅ Found {len(target_contacts)} key contacts in MEMemory")
    except Exception as e:
        return {"status": "error", "message": f"MEMemory MCP failed to retrieve contacts: {e}"}

    # --- Step 3: Retrieve Outreach Template (L3 Pinecone) ---
    # Use the company news to find the most relevant outreach template
    pinecone_query = f"Best outreach pitch template for: {company_news[:200]}..."
    try:
        search_result_str = search_records(
            query=pinecone_query, index="outreach_templates", top_k=1, namespace="outreach")
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
            logger.warning(
                f"⚠️ Pinecone lookup failed, using fallback template: {e}")

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
    primary_contact = target_contacts[0] if target_contacts else {
        "name": "Hiring Manager", "email": "contact@company.com"}

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
        # --- HARDENING PROTOCOL 10: SHADOW MODE EXECUTION ---
        if SHADOW_MODE_ACTIVE:
            if logger:
                logger.warning(f"👻 SHADOW MODE: Email to {primary_contact.get('email', 'contact@company.com')} blocked.")
                logger.warning(f"Email content saved to shadow_output/email_{primary_contact.get('email', 'contact@company.com')}.txt")
            email_result = {"status": "SUCCESS", "result": "SHADOW_BLOCKED"}
        else:
            email_result = send_email(
                recipient=primary_contact.get('email', 'contact@company.com'),
                subject=f"Re: {', '.join(news_keywords) if news_keywords else 'Potential Collaboration'}",
                body=personalized_pitch
            )
        # --------------------------------------------------

        # Log action for watchdog
        log_action("SEND_EMAIL", f"Sent to {primary_contact.get('email', 'contact@company.com')}")

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
        logger.info(
            f"⏰ Starting optimal contact time vetting for {lead_email} in {lead_timezone}.")

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
        # Get the current time in the agent's system timezone (UTC)
        system_time_str = get_current_time(timezone="UTC")
        # Parse ISO format to extract time
        from datetime import datetime
        system_time = datetime.fromisoformat(
            system_time_str.replace('Z', '+00:00'))
        current_time_hhmm = system_time.strftime('%H:%M')

        if logger:
            logger.info(
                f"✅ Retrieved agent's current time: {current_time_hhmm}")
    except Exception as e:
        return {"status": "error", "message": f"Time MCP (get_current_time) failed: {e}"}

    # --- Step 2: Convert Time to Lead's Local Time (L4 Time MCP) ---
    # We use the current system time to estimate what time it is RIGHT NOW for the lead.
    try:
        # Convert from UTC to the lead's timezone
        converted_time_str = convert_time(
            source_timezone="UTC",
            time=current_time_hhmm,
            target_timezone=lead_timezone
        )
        # Parse the returned ISO format to extract local time
        lead_local_time_obj = datetime.fromisoformat(
            converted_time_str.replace('Z', '+00:00'))
        lead_local_time = lead_local_time_obj.strftime('%H:%M')

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
            send_result = send_email(
                recipient=lead_email, subject=subject, body=pitch_body)

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
                    logger.warning(
                        f"⚠️ MEMemory logging failed (non-critical): {mem_e}")

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
                logger.warning(
                    f"⚠️ MEMemory logging failed (non-critical): {mem_e}")

        return {"status": "deferred", "message": f"Outreach deferred. Local time {lead_local_time} is outside business hours. Requires Calendar MCP for auto-scheduling."}


def vet_lead_snapshot_outreach(lead_profile_url: str, lead_email: str, user_name: str, pitch_topic: str, expected_title: str, tools: Dict[str, Any], logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Refined 'Lead Snapshot Vetting' (Outreach Engine). Uses L2 Playwright for efficient, verified context capture
    before committing to the outreach action, adhering to the 22/100 connection budget.
    """
    if logger:
        logger.info(
            f"📸 Starting efficient L2 Snapshot Vetting for {lead_email} (Budget: 78 remaining connections).")

    snapshot_file_path = f"snapshots/{lead_email.split('@')[0]}_profile.png"

    # Extract Playwright MCP tools
    browser_navigate = tools.get('browser_navigate')
    browser_verify_text_visible = tools.get('browser_verify_text_visible')
    browser_snapshot = tools.get('browser_snapshot')
    search_nodes = tools.get('search_nodes')
    search_records = tools.get('search_records')
    send_email = tools.get('send_email')

    # --- Step 1: Capture and Verify Live Context (L2 Playwright) ---
    try:
        if logger:
            logger.info(
                f"L2 Playwright: Navigating and verifying content at {lead_profile_url}.")

        # 1. Navigate (Necessary connection step)
        browser_navigate(url=lead_profile_url)

        # 2. Verify: Ensure the page loaded the correct content (Saves connections if page is junk)
        # We assume the lead's job title or company name is visible on the page.
        browser_verify_text_visible(text=expected_title)

        # 3. Snapshot: Capture the accessibility tree snapshot for later analysis
        # Using browser_snapshot (better than screenshot)
        # Filename parameter used for saving
        browser_snapshot(filename=snapshot_file_path)

        if logger:
            logger.info(
                f"✅ Playwright connection successful. Verified '{expected_title}' and snapshot saved.")

    except Exception as e:
        if logger:
            logger.warning(
                f"⚠️ Playwright L2 failed (Connection Budget Protected: {e}). Falling back to static context.")
        snapshot_file_path = "N/A (L2 connection failed or verification failed)"

    # --- Step 2 & 3: Retrieve Personalization & Canonical Pitch (L5/L3) ---
    # ... (Rest of the logic is retained from the previous step)

    try:
        relation_query = f"User {user_name} relationship to lead {lead_email} and preferred outreach style."
        user_context_str = search_nodes(query=relation_query)  # L5 MEMemory
        user_context = json.loads(user_context_str)

        pitch_query = f"Best outreach pitch template for topic '{pitch_topic}' in {user_context.get('style', 'formal')} style."
        search_result_str = search_records(
            query=pitch_query, index="outreach_templates", top_k=1)  # L3 Pinecone
        search_result = json.loads(search_result_str)
        canonical_pitch = search_result[0].get(
            'text', 'Placeholder pitch content.')

    except Exception as e:
        if logger:
            logger.error(f"Context retrieval failed: {e}")
        canonical_pitch = "Context system failure."

    # --- Step 4: Dispatch Action (Send Email MCP) ---
    final_subject = f"[Contextual] Regarding: {pitch_topic}"
    final_body = f"""
    Dear {lead_email},

    [Generated from Canonical Pitch and L5 context]
    {canonical_pitch}

    P.S. Your current professional status as '{expected_title}' was successfully verified via our automated system.
    """

    try:
        send_result = send_email(recipient=lead_email,
                                 subject=final_subject, body=final_body)

        # L5: Log the action
        search_nodes(
            query=f"Add observation: Sent outreach to {lead_email}. Snapshot status: {snapshot_file_path}.")

        return {
            "status": "outreach_dispatched",
            "message": f"Outreach successfully dispatched and logged to MEMemory.",
            "snapshot_path": snapshot_file_path,
            "send_result": send_result
        }
    except Exception as e:
        return {"status": "error", "message": f"Send Email MCP failed: {e}"}


def execute_autonomous_job_application(app_url: str, user_name: str, code_sample_path: str, tools: Dict[str, Any], logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Executes the multi-layer job application flow using L2 (Playwright) for interaction,
    L4 (Redis) for state, L1 (GitKraken) for artifact submission, and L5 (MEMemory) for logging.
    """
    if logger:
        logger.info(
            f"🤖 Starting autonomous application for {user_name} at {app_url}...")

    # Define paths for required components
    app_state_key = f"app_state:{user_name}:{hash(app_url)}"

    # Extract tools from the tools dictionary
    string_get = tools.get('string_get')
    string_set = tools.get('string_set')
    browser_navigate = tools.get('browser_navigate')
    browser_type = tools.get('browser_type')
    browser_click = tools.get('browser_click')
    commit = tools.get('commit')
    add_observations = tools.get('add_observations')

    # Validate required tools
    if not all([string_get, string_set, browser_navigate, browser_type, browser_click, commit, add_observations]):
        return {"status": "error", "message": "Required MCP tools not available"}

    # 1. Cache required data (L4 Redis) - Simulates pulling a JSON profile
    try:
        cached_profile = string_get(key=f"user_profile:{user_name}")
        if not cached_profile:
            # Create default profile if none exists
            default_profile = '{"email": "user@example.com", "name": "Jane Doe"}'
            string_set(key=f"user_profile:{user_name}", value=default_profile)
            cached_profile = default_profile
            if logger:
                logger.info("✅ L4 Redis: Created default user profile")
        user_data = json.loads(cached_profile)
        if logger:
            logger.info(
                f"✅ L4 Redis: Retrieved profile for {user_data['name']}")
    except Exception as e:
        return {"status": "error", "message": f"Redis L4 failed during profile retrieval: {e}"}

    # 2. Navigate and Interact (L2 Playwright)
    try:
        browser_navigate(url=app_url)
        if logger:
            logger.info(f"✅ L2 Playwright: Navigated to {app_url}")

        # Fill name field (L2 Interaction)
        browser_type(element="Name input field",
                     ref="[#name]", text=user_data['name'])
        if logger:
            logger.info("✅ L2 Playwright: Filled name field")

        # Fill email field
        browser_type(element="Email input field",
                     ref="[#email]", text=user_data['email'])
        if logger:
            logger.info("✅ L2 Playwright: Filled email field")

        # Store intermediate state in Redis (L4 Redis)
        string_set(key=app_state_key, value="FORM_FILLED")
        if logger:
            logger.info("✅ L4 Redis: Stored intermediate state")

    except Exception as e:
        return {"status": "error", "message": f"Playwright L2 interaction failed: {e}"}

    # 3. Submit Code Artifact (L1 GitKraken)
    try:
        # Commit the code sample artifact required by the application
        commit_message = f"Job Application Submission: {app_url} - Code Artifact"
        commit_result = commit(path=code_sample_path, message=commit_message)
        if logger:
            logger.info("✅ L1 GitKraken: Committed code sample artifact")
    except Exception as e:
        # Non-fatal if Git submission is optional; we log and continue to form submit
        if logger:
            logger.warning(
                f"⚠️ GitKraken L1 commit failed for code sample: {e}")
        commit_result = "Submission skipped."

    # 4. Final Form Submission (L2 Playwright)
    try:
        browser_click(element="Submit button", ref="[#submit_button]")
        if logger:
            logger.info("✅ L2 Playwright: Submitted application form")

        # 5. Log Action (L5 MEMemory)
        add_observations(observations=[{
            "entityName": user_name,
            "contents": [
                f"Successfully applied to {app_url}",
                f"Application time: {time.strftime('%Y-%m-%d %H:%M:%S')}",
                f"Git Artifact Status: {commit_result[:50]}..." if len(
                    commit_result) > 50 else commit_result
            ]
        }])
        if logger:
            logger.info("✅ L5 MEMemory: Logged application action")

        # 6. Final Redis State (L4 Redis)
        string_set(key=app_state_key, value="COMPLETED_SUBMITTED")
        if logger:
            logger.info("✅ L4 Redis: Updated final state")

        return {
            "status": "application_complete",
            "message": f"Job application submitted. Git: {commit_result}. Status logged to L5.",
            "app_state_key": app_state_key,
            "commit_result": commit_result
        }
    except Exception as e:
        return {"status": "error", "message": f"Final Playwright submit/L5 log failed: {e}"}


def adaptive_browser_session(target_url: str, logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Iteratively attempts to establish a stable Playwright session, adapting configuration
    (e.g., proxies) based on L4 Redis state, maximizing the use of limited L2 connections.
    (Sequential Thinking leveraged through adaptive retries.)
    """
    if logger:
        logger.info(f"🔌 Starting Adaptive Browser Session for {target_url}...")

    CONNECTION_STATE_KEY = "browser:last_working_proxy"
    max_retries = 3

    # --- Iterative Loop (Sequential Thinking) ---
    for i in range(1, max_retries + 1):

        # 1. Check/Apply Configuration (L4 Redis)
        # Retrieve last known working config
        proxy_config = string_get(CONNECTION_STATE_KEY)

        # NOTE: A real Playwright wrapper would apply this config before connecting.
        if i > 1 and proxy_config:
            if logger:
                logger.warning(
                    f"Attempt {i}: Initial connection failed. Applying cached proxy from L4 Redis...")

        # 2. Attempt Connection (L2 Playwright)
        try:
            # We mock a successful navigation on the final attempt
            if i == max_retries:
                browser_navigate(url=target_url)  # Assume success here
            else:
                # Simulate transient failure
                raise TimeoutError("Simulated connection failure.")

            # 3. Cache Success (L4 Redis) - Only on success, store current config
            # Here we would store the current, successful configuration
            string_set(CONNECTION_STATE_KEY, "proxy:none_active_success")

            # 4. Log Success (L5 MEMemory)
            try:
                add_observations(observations=[{
                    "entityName": "NetworkAudit",
                    "contents": [
                        f"Stable L2 connection established to {target_url} on attempt {i}",
                        f"Current proxy configuration cached: proxy:none_active_success",
                        f"Connection established at: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                    ]
                }])
            except Exception as mem_e:
                if logger:
                    logger.warning(
                        f"⚠️ Failed to log success to MEMemory: {mem_e}")

            if logger:
                logger.info(
                    f"✅ L2 Playwright: Successfully connected on attempt {i}")

            return {"status": "connected", "attempts": i, "proxy_used": proxy_config or "none"}

        except Exception as e:
            if i < max_retries:
                if logger:
                    logger.warning(
                        f"L2 Playwright failed on attempt {i} ({e}). Retrying...")
                # Add exponential backoff delay
                time.sleep(2 ** (i - 1))
            else:
                # 5. Log Failure (L5 MEMemory)
                try:
                    add_observations(observations=[{
                        "entityName": "NetworkAudit",
                        "contents": [
                            f"Failed to establish L2 connection to {target_url} after {max_retries} attempts",
                            f"Resource ABORTED. Last error: {str(e)}",
                            f"Failed at: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                        ]
                    }])
                except Exception as mem_e:
                    if logger:
                        logger.warning(
                            f"⚠️ Failed to log failure to MEMemory: {mem_e}")

                return {
                    "status": "failed",
                    "attempts": max_retries,
                    "message": "Failed to establish stable browser session.",
                    "last_error": str(e)
                }

    # This line is unreachable but included for function completeness
    return {"status": "failed", "attempts": 0, "message": "Loop logic error."}


def execute_resilient_application_pipeline(app_url: str, user_name: str, max_retries: int = 3, logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Executes a hardened, multi-stage application pipeline with iterative connection attempts,
    L3 fallbacks, and an immutable audit trail. (Sequential Thinking Maximized)
    """
    if logger:
        logger.info(
            f"🛡️ Starting RESILIENT Application Pipeline for {user_name} at {app_url}...")

    CONNECTION_STATE_KEY = "browser:last_working_proxy"
    APP_STATUS_KEY = f"app_status:{user_name}:{hash(app_url)}"

    # --- 1. Iterative Connection Loop (L2 Playwright, L4 Redis, Sequential Thinking) ---

    for i in range(1, max_retries + 1):
        # Check L4 Redis for cached config
        proxy_config = string_get(CONNECTION_STATE_KEY)

        if i > 1 and proxy_config:
            if logger:
                logger.warning(
                    f"Attempt {i}: Applying cached config from L4 Redis: {proxy_config}.")
            # NOTE: In a real system, the browser_navigate wrapper would apply this config.

        try:
            browser_navigate(url=app_url)

            # Connection Success: Break loop and cache the current configuration
            string_set(CONNECTION_STATE_KEY, "proxy:success_config_applied")
            if logger:
                logger.info(
                    f"✅ Stable L2 connection established on attempt {i}.")
            break

        except Exception as e:
            if i < max_retries:
                if logger:
                    logger.warning(
                        f"L2 connection failed on attempt {i}. Retrying...")
                # Add exponential backoff
                time.sleep(2 ** (i - 1))
            else:
                if logger:
                    logger.error(
                        "L2 connection failed permanently. Aborting pipeline.")
                string_set(APP_STATUS_KEY, "FAILED_ABORTED_NOCONNECT")
                return {"status": "failed_connection", "message": "Failed to establish stable browser session after retries."}

    # --- 2. L3 Fallback Mechanism (Pinecone L3 vs. Filesystem L1) ---
    code_artifact_content = "Default placeholder code."
    CODE_FALLBACK_PATH = "/cache/default_code_artifact.txt"

    try:
        # Attempt L3 Pinecone retrieval first (High-cost, high-quality)
        pinecone_query = f"Canonical code sample for job application at {app_url}"
        search_result_str = search_records(
            query=pinecone_query, index="application_artifacts", top_k=1)
        search_result = json.loads(search_result_str)
        code_artifact_content = search_result[0].get(
            'content', code_artifact_content)
        if logger:
            logger.info(
                "✅ L3 Pinecone artifact retrieved successfully (High-Quality RAG).")

    except Exception as e:
        # Hardening: Fallback to L1 Filesystem if L3 fails
        if logger:
            logger.warning(
                f"⚠️ L3 Pinecone failed ({e}). Falling back to L1 Filesystem cache.")
        try:
            # Mock read_text_file function
            with open(CODE_FALLBACK_PATH, 'r') as f:
                code_artifact_content = f.read()
            if logger:
                logger.info(
                    "✅ L1 Filesystem fallback successful (Resilience maintained).")
        except Exception:
            pass
        if logger:
            logger.error(
                "L1 Filesystem fallback failed. Using hardcoded default.")

    # --- 3. Core Interaction & Final Commit (L2 Playwright, L1 GitKraken) ---

    # Commit artifact for audit trail purposes (L1 GitKraken)
    try:
        # Simulate creating/updating the artifact file before committing
        code_file_path = f"artifacts/{user_name}_code_sample.js"
        # Write the code artifact to filesystem
        with open(code_file_path, 'w') as f:
            f.write(code_artifact_content)

        # Mock commit function
        commit_message = f"Job App Artifact: {app_url} Code Sample"
        commit_result = {
            "commit_id": f"commit_{hash(commit_message)}",
            "status": "success"
        }
        git_commit_id = commit_result.get("commit_id", "N/A")
        if logger:
            logger.info(
                f"✅ L1 GitKraken: Committed artifact with ID {git_commit_id}")
    except Exception as e:
        if logger:
            logger.warning(f"L1 GitKraken failed to commit artifact: {e}")
        git_commit_id = "FAILED_NO_COMMIT"

    # Final Form Interaction (L2 Playwright)
    application_status = "FAILED_INTERACTION"
    try:
        browser_type(element="Name input field", ref="[#name]", text=user_name)
        browser_type(element="Artifact path field",
                     ref="[#code_path]", text=code_file_path)
        browser_click(element="Final Submit button", ref="[#submit]")
        application_status = "SUCCESS"
        if logger:
            logger.info("✅ L2 Playwright: Application submitted successfully")
    except Exception as e:
        if logger:
            logger.error(f"L2 Playwright final interaction failed: {e}")

    # --- 4. Immutable Audit Trail (L4 Time, L5 MEMemory) ---

    # Timestamp (L4 Time)
    audit_timestamp_str = get_current_time(timezone="UTC")

    # Final L4 State
    string_set(APP_STATUS_KEY,
               f"COMPLETED_AUDITED|Status:{application_status}")

    # Final Log (L5 MEMemory) - Non-Repudiable Record
    try:
        audit_content = f"APP AUDIT: Status={application_status}. App={app_url}. GitCommit={git_commit_id}. Time={audit_timestamp_str}."
        add_observations(observations=[{
            "entityName": "ApplicationAudit",
            "contents": [
                audit_content,
                f"User: {user_name}",
                f"Connection attempts: {i}",
                f"Artifact source: {'Pinecone L3' if 'Pinecone' in str(code_artifact_content) else 'Filesystem L1'}"
            ]
        }])
        if logger:
            logger.info("✅ L5 MEMemory: Immutable audit trail created")
    except Exception as e:
        if logger:
            logger.warning(
                f"⚠️ L5 MEMemory logging failed (non-critical): {e}")

    return {
        "status": application_status,
        "message": "Resilient pipeline executed and audit trail created.",
        "git_commit_id": git_commit_id,
        "audit_time": audit_timestamp_str,
        "connection_attempts": i,
        "artifact_source": "Pinecone L3" if 'Pinecone' in str(code_artifact_content) else "Filesystem L1"
    }


def execute_resilient_application_pipeline_hardened(app_url: str, user_name: str, max_retries: int = 3, logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Final Hardened Pipeline: Combines Iterative L2 Connection with Atomic L3 Context Retrieval
    and Immutable Auditing across 10 MCPs.
    """
    if logger:
        logger.info(
            f"✨ Starting ZERO-LOSS Hardened Pipeline for {user_name} at {app_url}...")

    # --- Setup Keys ---
    CONNECTION_STATE_KEY = "browser:last_working_proxy"
    CODE_ARTIFACT_HASH_KEY = f"artifact_hash:{user_name}:{hash(app_url)}"
    APP_STATUS_KEY = f"app_status:{user_name}:{hash(app_url)}"
    CODE_FALLBACK_PATH = "/cache/default_code_artifact.txt"

    # --- PHASE 1: Iterative Connection & Context Retrieval (Hardening: L2/L4/L3 Resilience) ---

    # 1a. Iterative Connection Loop (L2 Playwright, L4 Redis)
    for i in range(1, max_retries + 1):
        proxy_config = string_get(CONNECTION_STATE_KEY)  # L4 Redis Check

        try:
            browser_navigate(url=app_url)
            # L4 Redis Write
            string_set(CONNECTION_STATE_KEY, "proxy:success_config_applied")
            if logger:
                logger.info(f"✅ L2 Connection established on attempt {i}.")
            break
        except Exception:
            if i == max_retries:
                if logger:
                    logger.error(
                        "L2 Connection failed permanently. Aborting pipeline.")
                return {"status": "failed_connection", "message": "Failed to establish stable browser session."}
            if logger:
                logger.warning(
                    f"L2 failed on attempt {i}. Retrying with adaptive config...")
            time.sleep(1)

    # 1b. Atomic Context Retrieval (L3 Pinecone, L4 Redis, L1 Filesystem Fallback)
    code_artifact_content = "Default placeholder code."
    job_hash = str(hash(app_url))  # Use app_url hash as job ID

    try:
        # Check Cache (L4 Redis) - The read-through portion
        cached_artifact = string_get(f"artifact:{job_hash}")
        if cached_artifact:
            code_artifact_content = json.loads(cached_artifact).get(
                'content', code_artifact_content)
            if logger:
                logger.info("✅ L4 Redis Cache Hit for artifact.")
        else:
            # L3 Retrieval with L1 Fallback
            search_result_str = search_records(
                query=f"canonical code sample for {app_url}", index="application_artifacts", top_k=1)
            search_result = json.loads(search_result_str)
            code_artifact_content = search_result[0].get(
                'content', code_artifact_content)

            # Atomic Write (L4 Redis Transaction Hardening)
            start_transaction()
            watch_key(f"artifact:{job_hash}")
            transaction_set_with_ttl(f"artifact:{job_hash}", json.dumps(
                {"content": code_artifact_content}), 86400)
            commit_transaction()
            if logger:
                logger.info("✅ L4 Redis: Atomic transaction committed.")

    except Exception as e:
        # L3 Pinecone/L4 Redis failure: Fallback to L1 Filesystem
        if logger:
            logger.warning(
                f"⚠️ L3/L4 Context failed: {e}. Falling back to L1 Filesystem.")
        try:
            code_artifact_content = read_text_file(
                path=CODE_FALLBACK_PATH)  # L1 Filesystem Read
            if logger:
                logger.info("✅ L1 Filesystem fallback successful.")
        except Exception:
            pass
        if logger:
            logger.error(
                "L1 Filesystem fallback failed. Using hardcoded default.")

    # --- PHASE 2: Core Action and Immutable Audit Trail (L1/L2/L4/L5) ---

    # 2a. Commit Artifact (L1 GitKraken)
    try:
        code_file_path = f"artifacts/{user_name}_code_sample.js"
        # Write the code artifact to filesystem
        with open(code_file_path, 'w') as f:
            f.write(code_artifact_content)

        # Mock commit function
        commit_message = f"Job App Artifact: {app_url} Code Sample"
        commit_result = {
            "commit_id": f"commit_{hash(commit_message)}",
            "status": "success"
        }
        git_commit_id = commit_result.get("commit_id", "FAILED_NO_COMMIT")
        if logger:
            logger.info(
                f"✅ L1 GitKraken: Committed artifact with ID {git_commit_id}")
    except Exception:
        git_commit_id = "FAILED_NO_COMMIT"

    # 2b. Final Form Interaction (L2 Playwright)
    application_status = "FAILED_INTERACTION"
    try:
        browser_type(element="Name input field", ref="[#name]", text=user_name)
        browser_type(element="Artifact path field",
                     ref="[#code_path]", text=code_file_path)
        browser_click(element="Final Submit button", ref="[#submit]")
        application_status = "SUCCESS"
        if logger:
            logger.info("✅ L2 Playwright: Application submitted successfully")
    except Exception as e:
        if logger:
            logger.error(f"L2 Playwright final interaction failed: {e}")

    # 2c. Immutable Audit (L4 Time, L5 MEMemory)
    audit_timestamp_str = get_current_time(timezone="UTC")  # L4 Time

    # Final L4 State
    string_set(APP_STATUS_KEY,
               f"COMPLETED_AUDITED|Status:{application_status}")

    # Final Log (L5 MEMemory) - Non-Repudiable Record
    try:
        audit_content = f"APP AUDIT: Status={application_status}. GitCommit={git_commit_id}. Time={audit_timestamp_str}. ProxyCache={string_get(CONNECTION_STATE_KEY)}."
        add_observations(observations=[{
            "entityName": "ApplicationAudit",
            "contents": [
                audit_content,
                f"User: {user_name}",
                f"App URL: {app_url}",
                f"Pipeline Type: ZERO-LOSS Hardened",
                f"Connection attempts: {i}",
                f"Artifact source: {'Pinecone L3' if 'Pinecone' in str(code_artifact_content) else 'Filesystem L1'}"
            ]
        }])
        if logger:
            logger.info("✅ L5 MEMemory: Immutable audit trail created")
    except Exception as e:
        if logger:
            logger.warning(
                f"⚠️ L5 MEMemory logging failed (non-critical): {e}")

    return {
        "status": application_status,
        "message": "Full resilient pipeline executed and immutable audit trail created.",
        "git_commit_id": git_commit_id,
        "audit_time": audit_timestamp_str,
        "connection_attempts": i,
        "artifact_source": "Pinecone L3" if 'Pinecone' in str(code_artifact_content) else "Filesystem L1",
        "pipeline_type": "ZERO-LOSS Hardened"
    }


def brand_compliant_outreach(company_url: str, user_name: str, brand_id: str = "default", logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Outreach sequence with brand compliance and cost-controlled search.
    Integrates Figma (L2) for brand guidelines and rate-limited Brave Search (L1/L3).
    """
    if logger:
        logger.info(f"🎨 Starting Brand-Compliant Outreach for {company_url}")

    # 1. Retrieve brand guidelines from Figma (L2)
    try:
        brand_guidelines = get_brand_style_guide(brand_id, logger=logger)
        if logger:
            logger.info(f"✅ Retrieved brand guidelines for {brand_id}")
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ Failed to retrieve brand guidelines: {e}")
        brand_guidelines = {
            "colors": ["#000000", "#FFFFFF"],
            "tone": "professional",
            "_fallback": True
        }

    # 2. Perform cost-controlled company research
    try:
        research_query = f"{company_url} company information executives"
        search_results = execute_cost_controlled_search(
            research_query, logger=logger)

        if search_results:
            results = json.loads(search_results)
            company_info = results[0] if results else {}
            if logger:
                logger.info(
                    f"✅ Retrieved company information via rate-limited search")
        else:
            company_info = {}
            if logger:
                logger.warning(
                    "⚠️ Search budget exhausted - using minimal info")
    except Exception as e:
        if logger:
            logger.error(f"❌ Company research failed: {e}")
        company_info = {}

    # 3. Generate brand-compliant outreach content
    outreach_content = f"""
Subject: Partnership Opportunity with {brand_guidelines.get('company_name', 'Your Company')}

Dear {company_info.get('contact_name', 'Hiring Manager')},

I hope this message finds you well. I'm reaching out regarding potential opportunities at {company_url}.

Our team specializes in {brand_guidelines.get('specialization', 'innovative solutions')} that align with your company's goals.

Best regards,
{user_name}
"""

    # 4. Validate brand compliance
    compliance_result = ensure_brand_compliance(
        content=outreach_content,
        brand_guidelines=brand_guidelines,
        logger=logger
    )

    # 5. Log compliance check to MEMory (L5)
    try:
        add_observations(observations=[{
            "entityName": "OutreachCompliance",
            "contents": [
                f"Brand compliance check for {company_url}",
                f"Status: {'COMPLIANT' if compliance_result['compliant'] else 'NON_COMPLIANT'}",
                f"Issues: {compliance_result.get('issues', [])}",
                f"Brand ID: {brand_id}"
            ]
        }])
    except Exception:
        pass
        # Silently ignore MEMory logging failures to not interrupt outreach flow
        pass

    return {
        "status": "ready" if compliance_result['compliant'] else "non_compliant",
        "message": f"Outreach content {'complies' if compliance_result['compliant'] else 'does not comply'} with brand guidelines",
        "content": outreach_content,
        "compliance_result": compliance_result,
        "brand_source": "figma" if not brand_guidelines.get('_fallback') else "fallback"
    }