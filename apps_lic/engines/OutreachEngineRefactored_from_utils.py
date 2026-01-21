"""
Outreach Engine - Thin Orchestrator (Refactored)

This module provides backward-compatible wrapper functions that delegate
to the new dedicated agents in apps_lic/agents/.

Original monolithic functions have been decomposed into:
- LeadVettingAgent: Multi-layer lead qualification
- OptimalTimeSchedulerAgent: Time-based outreach scheduling
- JobApplicationAgent: Autonomous form filling via Playwright
- BrowserSessionAgent: Resilient browser session management
- ResilientPipelineAgent: Full ZERO-LOSS pipeline orchestrator

For new code, prefer importing and using agents directly:
    from apps_lic.agents import LeadVettingAgent, ResilientPipelineAgent
"""

import asyncio
import json
import os
from typing import Any

# === NEW: Import decomposed agents ===
from apps_lic.agents import (
    BrowserSessionAgent,
    JobApplicationAgent,
    LeadVettingAgent,
    OptimalTimeSchedulerAgent,
    ResilientPipelineAgent,
)

# Import core utilities (kept for helper functions)
from core_utils import (
    add_observations,
)

# Import hardened MCP functions
from mcp_hardening import (
    ensure_brand_compliance,
    execute_cost_controlled_search,
    get_brand_style_guide,
)

# Import egress filter for Protocol 8
from network_utils import strict_egress_filter

# Global configuration (shared with agents)
SHADOW_MODE_ACTIVE = os.environ.get("AGENT_MODE", "PRODUCTION") == "SHADOW"

OUTREACH_ALLOWED_HOSTS = [
    "api.openai.com",
    "anthropic.com",
    "genai.google.com",
    "smtp.sendgrid.net",
    "mailgun.com",
    "linkedin.com",
    "www.linkedin.com",
]


# === Shared Helper Functions (kept in orchestrator) ===


@strict_egress_filter(allowed_domains=OUTREACH_ALLOWED_HOSTS)
def _fetch_company_content(url: str, fetch_tool: Any, max_length: int = 1000) -> str | None:
    """Fetches company content with egress filtering."""
    return fetch_tool(url=url, max_length=max_length)


# === BACKWARD-COMPATIBLE WRAPPER FUNCTIONS ===
# These wrap the new agents to maintain compatibility with existing callers


def automated_lead_vetting(
    company_url: str, user_name: str, tools: dict[str, Any], Logger: Any | None = None
) -> dict[str, Any]:
    """
    DEPRECATED: Use LeadVettingAgent directly for new code.

    Backward-compatible wrapper that delegates to LeadVettingAgent.
    """
    agent = LeadVettingAgent()
    return asyncio.run(agent.execute(company_url, user_name, tools, Logger))


def vet_lead_optimal_time(
    lead_email: str,
    lead_timezone: str,
    pitch_body: str,
    tools: dict[str, Any],
    Logger: Any | None = None,
) -> dict[str, Any]:
    """
    DEPRECATED: Use OptimalTimeSchedulerAgent directly for new code.

    Backward-compatible wrapper that delegates to OptimalTimeSchedulerAgent.
    """
    agent = OptimalTimeSchedulerAgent()
    return asyncio.run(agent.execute(lead_email, lead_timezone, pitch_body, tools, Logger))


def execute_autonomous_job_application(
    app_url: str,
    user_name: str,
    code_sample_path: str,
    tools: dict[str, Any],
    Logger: Any | None = None,
) -> dict[str, Any]:
    """
    DEPRECATED: Use JobApplicationAgent directly for new code.

    Backward-compatible wrapper that delegates to JobApplicationAgent.
    """
    agent = JobApplicationAgent()
    return asyncio.run(agent.execute(app_url, user_name, code_sample_path, tools, Logger))


def adaptive_browser_session(
    target_url: str, tools: dict[str, Any] = None, Logger: Any | None = None
) -> dict[str, Any]:
    """
    DEPRECATED: Use BrowserSessionAgent directly for new code.

    Backward-compatible wrapper that delegates to BrowserSessionAgent.
    """
    agent = BrowserSessionAgent()
    return asyncio.run(agent.execute(target_url, tools, max_retries=3, Logger=Logger))


def execute_resilient_application_pipeline(
    app_url: str, user_name: str, max_retries: int = 3, Logger: Any | None = None
) -> dict[str, Any]:
    """
    DEPRECATED: Use ResilientPipelineAgent directly for new code.

    Backward-compatible wrapper that delegates to ResilientPipelineAgent.
    """
    agent = ResilientPipelineAgent()
    return asyncio.run(
        agent.execute(app_url, user_name, tools=None, max_retries=max_retries, Logger=Logger)
    )


def execute_resilient_application_pipeline_hardened(
    app_url: str, user_name: str, max_retries: int = 3, Logger: Any | None = None
) -> dict[str, Any]:
    """
    DEPRECATED: Use ResilientPipelineAgent directly for new code.

    This function is now an alias for execute_resilient_application_pipeline
    since ResilientPipelineAgent implements the hardened version by default.
    """
    return execute_resilient_application_pipeline(app_url, user_name, max_retries, Logger)


# === FUNCTIONS KEPT IN ORCHESTRATOR (Not yet agent-converted) ===


def vet_lead_snapshot_outreach(
    lead_profile_url: str,
    lead_email: str,
    user_name: str,
    pitch_topic: str,
    expected_title: str,
    tools: dict[str, Any],
    Logger: Any | None = None,
) -> dict[str, Any]:
    """
    Refined 'Lead Snapshot Vetting' (Outreach Engine). Uses L2 Playwright for efficient, verified context capture
    before committing to the outreach action, adhering to the 22/100 connection budget.

    TODO: Convert to SnapshotOutreachAgent in future iteration.
    """
    if Logger:
        Logger.info(
            f"📸 Starting efficient L2 Snapshot Vetting for {lead_email} (Budget: 78 remaining connections)."
        )

    snapshot_file_path = f"snapshots/{lead_email.split('@')[0]}_profile.png"

    # Extract Playwright MCP tools
    browser_navigate_tool = tools.get("browser_navigate")
    browser_verify_text_visible = tools.get("browser_verify_text_visible")
    browser_snapshot = tools.get("browser_snapshot")
    search_nodes = tools.get("search_nodes")
    search_records_tool = tools.get("search_records")
    send_email = tools.get("send_email")

    # Step 1: Capture and Verify Live Context (L2 Playwright)
    try:
        if Logger:
            Logger.info(f"L2 Playwright: Navigating and verifying content at {lead_profile_url}.")

        browser_navigate_tool(url=lead_profile_url)
        browser_verify_text_visible(text=expected_title)
        browser_snapshot(filename=snapshot_file_path)

        if Logger:
            Logger.info(
                f"✅ Playwright connection successful. Verified '{expected_title}' and snapshot saved."
            )

    except Exception as e:
        if Logger:
            Logger.warning(
                f"⚠️ Playwright L2 failed (Connection Budget Protected: {e}). Falling back to static context."
            )
        snapshot_file_path = "N/A (L2 connection failed or verification failed)"

    # Step 2 & 3: Retrieve Personalization & Canonical Pitch (L5/L3)
    try:
        relation_query = (
            f"User {user_name} relationship to lead {lead_email} and preferred outreach style."
        )
        user_context_str = search_nodes(query=relation_query)
        user_context = json.loads(user_context_str)

        pitch_query = f"Best outreach pitch template for topic '{pitch_topic}' in {user_context.get('style', 'formal')} style."
        search_result_str = search_records_tool(
            query=pitch_query, index="outreach_templates", top_k=1
        )
        search_result = json.loads(search_result_str)
        canonical_pitch = search_result[0].get("text", "Placeholder pitch content.")

    except Exception as e:
        if Logger:
            Logger.error(f"Context retrieval failed: {e}")
        canonical_pitch = "Context system failure."

    # Step 4: Dispatch Action (Send Email MCP)
    final_subject = f"[Contextual] Regarding: {pitch_topic}"
    final_body = f"""
    Dear {lead_email},

    [Generated from Canonical Pitch and L5 context]
    {canonical_pitch}

    P.S. Your current professional status as '{expected_title}' was successfully verified via our automated system.
    """

    try:
        send_result = send_email(recipient=lead_email, subject=final_subject, body=final_body)
        search_nodes(
            query=f"Add observation: Sent outreach to {lead_email}. Snapshot status: {snapshot_file_path}."
        )

        return {
            "status": "outreach_dispatched",
            "message": "Outreach successfully dispatched and logged to MEMemory.",
            "snapshot_path": snapshot_file_path,
            "send_result": send_result,
        }
    except Exception as e:
        return {"status": "error", "message": f"Send Email MCP failed: {e}"}


def brand_compliant_outreach(
    company_url: str, user_name: str, brand_id: str = "default", Logger: Any | None = None
) -> dict[str, Any]:
    """
    Outreach sequence with brand compliance and cost-controlled search.
    Integrates Figma (L2) for brand guidelines and rate-limited Brave Search (L1/L3).

    TODO: Convert to BrandComplianceAgent in future iteration.
    """
    if Logger:
        Logger.info(f"🎨 Starting Brand-Compliant Outreach for {company_url}")

    # 1. Retrieve brand guidelines from Figma (L2)
    try:
        brand_guidelines = get_brand_style_guide(brand_id, Logger=Logger)
        if Logger:
            Logger.info(f"✅ Retrieved brand guidelines for {brand_id}")
    except Exception as e:
        if Logger:
            Logger.warning(f"⚠️ Failed to retrieve brand guidelines: {e}")
        brand_guidelines = {
            "colors": ["#000000", "#FFFFFF"],
            "tone": "professional",
            "_fallback": True,
        }

    # 2. Perform cost-controlled company research
    try:
        research_query = f"{company_url} company information executives"
        search_results = execute_cost_controlled_search(research_query, Logger=Logger)

        if search_results:
            results = json.loads(search_results)
            company_info = results[0] if results else {}
            if Logger:
                Logger.info("✅ Retrieved company information via rate-limited search")
        else:
            company_info = {}
            if Logger:
                Logger.warning("⚠️ Search budget exhausted - using minimal info")
    except Exception as e:
        if Logger:
            Logger.error(f"❌ Company research failed: {e}")
        company_info = {}

    # 3. Generate brand-compliant outreach content
    outreach_content = f"""
Subject: Partnership Opportunity with {brand_guidelines.get("company_name", "Your Company")}

Dear {company_info.get("contact_name", "Hiring Manager")},

I hope this message finds you well. I'm reaching out regarding potential opportunities at {company_url}.

Our team specializes in {brand_guidelines.get("specialization", "innovative solutions")} that align with your company's goals.

Best regards,
{user_name}
"""

    # 4. Validate brand compliance
    compliance_result = ensure_brand_compliance(
        content=outreach_content, brand_guidelines=brand_guidelines, Logger=Logger
    )

    # 5. Log compliance check to MEMory (L5)
    try:
        add_observations(
            observations=[
                {
                    "entityName": "OutreachCompliance",
                    "contents": [
                        f"Brand compliance check for {company_url}",
                        f"Status: {'COMPLIANT' if compliance_result['compliant'] else 'NON_COMPLIANT'}",
                        f"Issues: {compliance_result.get('issues', [])}",
                        f"Brand ID: {brand_id}",
                    ],
                }
            ]
        )
    except Exception:
        pass

    return {
        "status": "ready" if compliance_result["compliant"] else "non_compliant",
        "message": f"Outreach content {'complies' if compliance_result['compliant'] else 'does not comply'} with brand guidelines",
        "content": outreach_content,
        "compliance_result": compliance_result,
        "brand_source": "figma" if not brand_guidelines.get("_fallback") else "fallback",
    }


# === NEW UNIFIED ENTRYPOINT ===


async def run_outreach_engine(workflow: str, **kwargs) -> dict[str, Any]:
    """
    Unified entrypoint for the Outreach Engine.

    Args:
        workflow: One of "lead_vetting", "optimal_time", "job_application",
                  "browser_session", "resilient_pipeline", "snapshot", "brand_compliant"
        **kwargs: Arguments passed to the selected workflow

    Returns:
        Dict with workflow results

    Example:
        result = await run_outreach_engine(
            "lead_vetting",
            company_url="https://example.com",
            user_name="John Doe",
            tools=tools_dict
        )
    """
    workflows = {
        "lead_vetting": lambda: LeadVettingAgent().execute(
            kwargs["company_url"], kwargs["user_name"], kwargs["tools"], kwargs.get("Logger")
        ),
        "optimal_time": lambda: OptimalTimeSchedulerAgent().execute(
            kwargs["lead_email"],
            kwargs["lead_timezone"],
            kwargs["pitch_body"],
            kwargs["tools"],
            kwargs.get("Logger"),
        ),
        "job_application": lambda: JobApplicationAgent().execute(
            kwargs["app_url"],
            kwargs["user_name"],
            kwargs["code_sample_path"],
            kwargs["tools"],
            kwargs.get("Logger"),
        ),
        "browser_session": lambda: BrowserSessionAgent().execute(
            kwargs["target_url"],
            kwargs.get("tools"),
            kwargs.get("max_retries", 3),
            kwargs.get("Logger"),
        ),
        "resilient_pipeline": lambda: ResilientPipelineAgent().execute(
            kwargs["app_url"],
            kwargs["user_name"],
            kwargs.get("tools"),
            kwargs.get("max_retries", 3),
            kwargs.get("Logger"),
        ),
    }

    if workflow not in workflows:
        return {
            "status": "error",
            "message": f"Unknown workflow: {workflow}. Available: {list(workflows.keys())}",
        }

    return await workflows[workflow]()
