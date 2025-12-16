"""
Hardened Outreach Engine - Integrates L3 RAG (Pinecone) and L4 LangCache
Enhanced with personalized content retrieval and intelligent caching
"""
import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Import Clarity & Brevity Filter for L1 content refinement
from clarity_brevity_filter import filter_content

# Import Intent Scoring Model for L4 cost governance
from intent_scoring_model import score_lead_intent

# Import News RAG for dynamic personalization
from news_rag_pipeline import execute_news_rag

# Import LangCache functions
from redis_langcache_pipeline import execute_temporal_rate_limiting

# Import temporal vetting
from temporal_vetting import vet_lead_optimal_time


def execute_hardened_outreach_sequence(
    lead_timezone: str,
    lead_profile: Dict[str, Any],  # New: Lead profile for personalization
    recipient_email: str,
    tools: Dict[str, Any],
    logger: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Hardened Outreach Engine with L3 RAG, L4 LangCache, Dynamic News RAG, Intent Scoring, and Clarity Filter integration.

    Flow:
    1. Rate Limiting Check (L4 Redis)
    2. Intent Scoring (L4 - Lead priority and reply likelihood)
    3. Personalized Content Retrieval (L3 Pinecone + L4 LangCache)
    4. Dynamic News RAG (L4 - Real-time context injection)
    5. Temporal Compliance Check (L4 Time)
    6. Clarity & Brevity Filter (L1 - NEW: Content refinement)
    7. Send Email (L1)
    8. Cache Success Pattern (L4 LangCache)
    9. Audit Log (L5 MEMemory)

    Args:
        lead_timezone: IANA timezone for the lead
        lead_profile: Dict containing lead info (industry, role, company, etc.)
        recipient_email: Target email address
        tools: Dictionary containing MCP tools
        logger: Optional logger instance

    Returns:
        Dictionary containing final status, personalization info, and audit data
    """
    if logger:
        logger.info(
            f"🛡️ Starting Hardened Outreach Sequence for {recipient_email}")

    # Extract required tools
    get_current_time = tools.get('get_current_time')
    send_email = tools.get('send_email')
    add_observations = tools.get('add_observations')
    search_records = tools.get('search_records')  # L3 Pinecone
    string_get = tools.get('string_get')         # L4 Redis
    string_set = tools.get('string_set')         # L4 Redis

    # Validate tools
    if not all([get_current_time, send_email, string_get, string_set]):
        return {
            "status": "ERROR_TOOLS_MISSING",
            "message": "Required MCP tools not available"
        }

    # Generate lead ID for rate limiting
    lead_id = hashlib.md5(
        f"{recipient_email}_{lead_profile.get('company', '')}".encode()).hexdigest()[:16]

    final_status = "PENDING"
    personalization_source = "NONE"
    cost_savings = []

    # --- 1. Rate Limiting Check (L4 Redis) ---
    try:
        rate_limit_result = execute_temporal_rate_limiting(
            lead_id=lead_id,
            action_type="outreach_email",
            max_actions_per_hour=2,  # Max 2 emails per hour per lead
            logger=logger
        )

        if rate_limit_result["status"] == "rate_limited":
            final_status = "RATE_LIMITED"
            if logger:
                logger.warning(f"⚠️ Rate limit exceeded for lead {lead_id}")
            return {
                "status": final_status,
                "message": rate_limit_result["message"],
                "reset_time": rate_limit_result.get("reset_time")
            }
    except Exception as e:
        if logger:
            logger.warning(f"Rate limiting failed: {e}")


    # --- 2. Intent Scoring (L4 - NEW: Lead priority and reply likelihood) ---
    intent_score = None
    intent_priority = "medium"

    try:
        # Mock engagement data (in production, this would come from CRM)
        engagement_data = {
            "previous_interactions": 0,  # New lead
            "email_open_rate": 0.0,
            "response_rate": 0.0,
            "days_since_last_contact": 999,  # Never contacted
            "contact_frequency": "low"
        }

        # Score lead intent
        intent_score = score_lead_intent(
            lead_id=lead_id,
            lead_profile=lead_profile,
            engagement_data=engagement_data,
            news_context={},  # Will be populated after News RAG
            personalization_data={},  # Will be populated after content retrieval
            logger=logger
        )

        intent_priority = intent_score.priority

        if logger:
            logger.info(
                f"🎯 Intent Score: {intent_score.overall_score}/100 ({intent_priority} priority)")
            logger.info(
                f"   Reply probability: {intent_score.reply_probability:.0%}")
            logger.info(f"   Recommended: {intent_score.recommended_action}")

        # Cost governance: Skip low-priority leads
        if intent_score.overall_score < 30:
            final_status = "LOW_PRIORITY_SKIPPED"
            if logger:
                logger.warning(
                    f"⚠️ Skipping low-priority lead (score: {intent_score.overall_score})")
            return {
                "status": final_status,
                "message": f"Lead score {intent_score.overall_score} below threshold",
                "intent_score": asdict(intent_score)
            }

        cost_savings.append(
            f"Intent scoring: Prioritized {intent_priority} leads")

    except Exception as e:
        if logger:
            logger.warning(f"⚠️ Intent scoring failed (non-critical): {e}")


    # --- 3. Personalized Content Retrieval (L3 Pinecone + L4 LangCache) ---
    personalized_pitch = None
    cache_key = f"outreach:template:{lead_profile.get('industry', 'general')}:{lead_profile.get('role', 'general')}"

    # Check LangCache first (cost governance)
    try:
        cached_template = string_get(cache_key)
        if cached_template:
            personalized_pitch = cached_template
            personalization_source = "LangCache"
            cost_savings.append("Pinecone query avoided")
            if logger:
                logger.info("✅ Template retrieved from LangCache (cost saved)")
    except Exception as e:
        if logger:
            logger.warning(f"LangCache check failed: {e}")


    # If not in cache, query Pinecone for personalized template
    if not personalized_pitch and search_records:
        try:
            # Build query based on lead profile
            query = f"Personalized outreach template for {lead_profile.get('role', 'professional')} in {lead_profile.get('industry', 'technology')} sector"

            # Search Pinecone for relevant templates
            search_result_str = search_records(
                query=query,
                index="outreach_templates",
                top_k=3,
                namespace="templates"
            )

            if search_result_str:
                search_results = json.loads(search_result_str)
                if search_results:
                    # Use the highest scoring template
                    best_template = search_results[0]
                    personalized_pitch = best_template.get('content', '')
                    personalization_source = "Pinecone"

                    # Cache the template for future use (24 hour TTL)
                    string_set(cache_key, personalized_pitch)

                    if logger:
                        logger.info(
                            f"✅ Retrieved template from Pinecone: {best_template.get('score', 'N/A')}")
        except Exception as e:
            if logger:
                logger.error(f"Pinecone search failed: {e}")


    # Fallback to default pitch if no personalized template found
    if not personalized_pitch:
        personalized_pitch = generate_default_pitch(lead_profile)
        personalization_source = "GENERATED"
        if logger:
            logger.info("ℹ️ Using generated default pitch")

    # --- 3. Dynamic News RAG (L4 - NEW: Real-time context injection) ---
    news_context = None
    news_personalization = []

    try:
        company = lead_profile.get('company', '')
        industry = lead_profile.get('industry', '')

        if company or industry:
            # Execute News RAG pipeline
            news_result = execute_news_rag(
                company=company,
                industry=industry,
                redis_get=string_get,
                redis_set=string_set,
                logger=logger
            )

            if news_result.get("news_available"):
                news_context = news_result.get("contextual_intro", "")
                news_personalization = news_result.get(
                    "personalization_points", [])

                # Update personalization source to include News RAG
                if personalization_source != "GENERATED":
                    personalization_source = f"{personalization_source}+NewsRAG"
                else:
                    personalization_source = "NewsRAG"

                # Inject news context into the pitch
                if news_context and personalized_pitch:
                    # Add contextual intro at the beginning
                    personalized_pitch = f"{news_context}\n\n{personalized_pitch}"

                # Add personalization points if available
                if news_personalization:
                    # Find a good place to insert personalization points
                    if "[Personalization Point]" in personalized_pitch:
                        # Replace placeholder with actual points
                        points_text = "\n".join(
                            [f"• {point}" for point in news_personalization[:2]])
                        personalized_pitch = personalized_pitch.replace(
                            "[Personalization Point]", points_text)
                    else:
                        # Append before closing
                        if news_personalization:
                            points_text = "\n".join(
                                [f"• {point}" for point in news_personalization[:2]])
                            personalized_pitch += f"\n\nPersonal notes:\n{points_text}"

                if logger:
                    logger.info(
                        f"✅ News RAG enhanced: {len(news_personalization)} insights added")
                    logger.info(
                        f"   Context: {news_context[:50]}..." if news_context else "")
                    cost_savings.append("News RAG: Real-time context added")
            else:
                if logger:
                    logger.info("ℹ️ No recent news found for personalization")
        else:
            if logger:
                logger.info(
                    "ℹ️ No company/industry info provided, skipping News RAG")

    except Exception as e:
        if logger:
            logger.warning(f"⚠️ News RAG failed (non-critical): {e}")
            # Continue without news context


    # --- 4. Temporal Compliance Check (L4 Time) ---
    try:
        time_str = get_current_time("UTC")
        current_utc_time_hm = datetime.fromisoformat(
            time_str.replace('Z', '+00:00')).strftime('%H:%M')

        if logger:
            logger.info(f"Current UTC time: {current_utc_time_hm}")
    except Exception as e:
        if logger:
            logger.error(f"Failed to get current time: {e}")
        return {
            "status": "ERROR_TIME_FETCH",
            "message": "Failed to retrieve current time"
        }


    # Temporal vetting
    vetting_result = vet_lead_optimal_time(
        lead_timezone, current_utc_time_hm, tools, logger)

    send_allowed = vetting_result['send_now']
    lead_local_time = vetting_result['lead_local_time']
    decision = vetting_result['decision']

    # --- 5. Clarity & Brevity Filter (L1 - NEW: Content refinement) ---
    clarity_result = None

    try:
        # Apply clarity and brevity filter to the personalized pitch
        clarity_result = filter_content(
            text=personalized_pitch,
            aggressive=False,  # Preserve personalization context
            preserve_personalization=True,
            logger=logger
        )

        # Use the filtered content
        personalized_pitch = clarity_result.filtered_text

        # Update personalization source to include clarity filter
        if personalization_source != "NONE":
            personalization_source = f"{personalization_source}+Clarity"
        else:
            personalization_source = "Clarity"

        if logger:
            logger.info(
                f"✅ Content refined: {clarity_result.word_count_reduction} words removed")
            logger.info(
                f"   Clarity score: {clarity_result.clarity_score:.2f}")
            logger.info(
                f"   Brevity score: {clarity_result.brevity_score:.2f}")

        cost_savings.append("Clarity filter: Improved message readability")

    except Exception as e:
        if logger:
            logger.warning(f"⚠️ Clarity filter failed (non-critical): {e}")
            # Continue with original content


    # --- 6. Send Email (if allowed) ---
    if send_allowed:
        try:
            # Personalize subject
            company = lead_profile.get('company', 'your company')
            role = lead_profile.get('role', 'professional')
            subject = f"Opportunity for {role} at {company}"

            # Send the personalized email
            email_result = send_email(
                recipient=recipient_email,
                subject=subject,
                body=personalized_pitch
            )

            final_status = "SENT_PERSONALIZED"

            # --- 5. Cache Success Pattern (L4 LangCache) ---
            if personalization_source == "Pinecone":
                # Increment template success counter
                success_key = f"outreach:success:{cache_key}"
                try:
                    current_success = int(string_get(success_key) or "0")
                    string_set(success_key, str(current_success + 1))
                    if logger:
                        logger.info(
                            f"✅ Template success cached: {current_success + 1} uses")
                except Exception as e:
                    if logger:
                        logger.warning(f"Success caching failed: {e}")


            if logger:
                logger.info(
                    f"✅ Personalized email sent. Source: {personalization_source}")

        except Exception as e:
            final_status = "SENT_FAILED"
            if logger:
                logger.error(f"❌ Email dispatch failed: {e}")
    else:
        final_status = "TEMPORAL_DELAY"
        next_send_time = calculate_next_business_time(
            lead_local_time, lead_timezone)

        if logger:
            logger.warning(f"⚠️ Temporal delay. Local time: {lead_local_time}")
            logger.info(f"💡 Next optimal send: {next_send_time}")

    # --- 6. Comprehensive Audit Log (L5 MEMemory) ---
    try:
        if add_observations:
            audit_data = {
                "status": final_status,
                "recipient": recipient_email,
                "lead_id": lead_id,
                "personalization_source": personalization_source,
                "industry": lead_profile.get('industry'),
                "role": lead_profile.get('role'),
                "company": lead_profile.get('company'),
                "timezone": lead_timezone,
                "local_time": lead_local_time,
                "decision": decision,
                "cost_savings": cost_savings,
                "news_rag_enabled": news_context is not None,
                "news_insights_count": len(news_personalization),
                "intent_score": intent_score.overall_score if intent_score else 0,
                "intent_priority": intent_priority,
                "reply_probability": intent_score.reply_probability if intent_score else 0,
                "clarity_filter_applied": clarity_result is not None,
                "clarity_score": clarity_result.clarity_score if clarity_result else 0,
                "brevity_score": clarity_result.brevity_score if clarity_result else 0,
                "words_removed": clarity_result.word_count_reduction if clarity_result else 0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            audit_message = f"HARDENED OUTREACH: {json.dumps(audit_data, separators=(',', ':'))}"

            add_observations(observations=[{
                "entityName": "HardenedOutreach",
                "contents": [audit_message]
            }])
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ Audit logging failed: {e}")


    # Build comprehensive result
    result = {
        "status": final_status,
        "lead_id": lead_id,
        "personalization_source": personalization_source,
        "lead_timezone": lead_timezone,
        "lead_local_time": lead_local_time,
        "decision": decision,
        "cost_savings": cost_savings,
        "message": f"Hardened sequence completed with status: {final_status}"
    }

    if final_status == "TEMPORAL_DELAY":
        result["next_optimal_send_time"] = calculate_next_business_time(
            lead_local_time, lead_timezone)

    if final_status in ["SENT_PERSONALIZED", "RATE_LIMITED"]:
        result["personalization_applied"] = True
        result["template_source"] = personalization_source

    return result


def generate_default_pitch(lead_profile: Dict[str, Any]) -> str:
    """Generate a default pitch based on lead profile."""
    role = lead_profile.get('role', 'professional')
    company = lead_profile.get('company', 'your organization')
    industry = lead_profile.get('industry', 'your field')

    return f"""Hello,

I hope this email finds you well. As a {role} at {company}, I thought you might be interested in exploring how we're helping leaders in the {industry} sector achieve their goals.

I'd love to share some insights that could be valuable to your work. Would you be open to a brief conversation next week?

Best regards,
[Your Name]"""


def calculate_next_business_time(current_local_time: str, timezone: str) -> str:
    """Calculate next optimal business time."""
    try:
        current_hour = int(current_local_time.split(':')[0])

        if current_hour < 9:
            return f"09:00 {timezone}"
        elif current_hour >= 17:
            return f"09:00 {timezone} (next business day)"
        else:
            return f"{current_local_time} {timezone}"
    except Exception:
        return f"09:00 {timezone} (next business day)"

# Test function


def test_hardened_outreach():
    """Test the hardened outreach engine."""
    # print("=== Hardened Outreach Engine Test ===\n")  # [Security Fix]

    # Mock tools
    def mock_get_current_time(tz):
        return "2025-12-15T14:00:00Z"

    def mock_send_email(recipient, subject, body):
        return f"Email sent to {recipient}"

    def mock_add_observations(observations):
        pass

    def mock_search_records(query, index, top_k, namespace):
        return json.dumps([{
            "content": "Personalized tech outreach template with industry-specific insights...",
            "score": 0.95,
            "metadata": {"industry": "technology", "role": "engineer"}
        }])

    def mock_string_get(key):
        return None  # No cache hit

    def mock_string_set(key, value):
        pass

    mock_tools = {
        'get_current_time': mock_get_current_time,
        'send_email': mock_send_email,
        'add_observations': mock_add_observations,
        'search_records': mock_search_records,
        'string_get': mock_string_get,
        'string_set': mock_string_set
    }

    # Test lead profile
    lead_profile = {
        "industry": "technology",
        "role": "Software Engineer",
        "company": "TechCorp",
        "seniority": "Senior"
    }

    # Execute test
    result = execute_hardened_outreach_sequence(
        lead_timezone="America/New_York",
        lead_profile=lead_profile,
        recipient_email="engineer@techcorp.com",
        tools=mock_tools,
        logger=None
    )

    # Display results
    # print(f"Status: {result['status']}")  # [Security Fix]
    # print(f"Personalization Source: {result['personalization_source']}")  # [Security Fix]
    # print(f"Lead ID: {result['lead_id']}")  # [Security Fix]
    # print(f"Decision: {result['decision']}")  # [Security Fix]
    # print(f"Cost Savings: {result['cost_savings']}")  # [Security Fix]

    return result


if __name__ == "__main__":
    test_hardened_outreach()

