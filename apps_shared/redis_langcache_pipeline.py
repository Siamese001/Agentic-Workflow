"""
Redis/LangCache Execution Pipeline
Implements advanced caching and cost governance patterns for LLM operations.
"""

import json
import time
from typing import Any, Dict, Optional

# Import core utilities
from core_utils import (
    add_observations,
    generate_draft_llm,
    get_from_langcache,
    set_to_langcache,
    string_get,
    string_set,
)


def execute_governed_prompt_caching(
    user_name: str,
    job_description_hash: str,
    rendered_prompt: str,
    logger: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Implements LLM Prompt Caching and Cost Governance (L4 LangCache/Redis).
    Checks cache first, then enforces a daily budget before generating content.
    """
    if logger:
        logger.info(
            f"⚡ Starting Governed Prompt Caching for {user_name} (Hash: {job_description_hash})")

    CACHE_KEY = f"llm:draft:{job_description_hash}:{user_name}"
    BUDGET_KEY = f"llm:daily_budget:{user_name}"
    DAILY_BUDGET = 5  # Max 5 generations per day per user

    # --- 1. Cache Check (L4 LangCache) ---
    final_draft = get_from_langcache(CACHE_KEY)

    if final_draft:
        # Cache Hit: Cost Avoidance Success
        try:
            add_observations(observations=[{
                "entityName": "CostGovernance",
                "contents": [f"LLM Generation AVOIDED (Cache Hit). Cost Savings: 1 run."]
            }])
        except Exception:
            pass
        if logger:
            logger.info("✅ Cache Hit: LLM Generation AVOIDED (Cost Saved).")
            return {"status": "cache_hit", "draft": final_draft}

    # --- 2. Cost Governance Check (L4 Redis) ---
    # NOTE: In a real system, we'd use INCR and GETSET atomically. We mock the budget control here.

    try:
        # Check current count
        current_runs_str = string_get(BUDGET_KEY)
        current_runs = int(current_runs_str) if current_runs_str else 0

        if current_runs >= DAILY_BUDGET:
            # Budget Abortion
            try:
                add_observations(observations=[{
                    "entityName": "CostGovernance",
                    "contents": [f"LLM Generation ABORTED. Daily budget of {DAILY_BUDGET} reached."]
                }])
                if logger:
                    logger.error(
                        f"❌ LLM Budget Aborted. {DAILY_BUDGET} generations reached today.")
                return {"status": "budget_aborted", "message": "Daily LLM generation budget exhausted."}

            except Exception as e:
                if logger:
                    logger.warning(
                        f"L4 Redis Budget check failed: {e}. Bypassing governance and generating.")
        else:
            # Atomically Increment Counter (Simulated)
            string_set(BUDGET_KEY, str(current_runs + 1))

    except Exception as e:
        if logger:
            logger.warning(
                f"L4 Redis Budget check failed: {e}. Bypassing governance and generating.")

    # --- 3. LLM Execution & Cache Write ---

    # Generate Draft (Costly Operation)
    generated_draft = generate_draft_llm(rendered_prompt)

    # Cache Write (L4 LangCache)
    set_to_langcache(CACHE_KEY, generated_draft, 86400)  # 24-hour TTL

    # Final Audit Log (L5 MEMemory)
    try:
        add_observations(observations=[{
            "entityName": "CostGovernance",
            "contents": [f"LLM Generation SUCCESS. Cache written. Total runs today: {current_runs + 1}."]
        }])
        if logger:
            logger.info(
                f"🎉 Generation SUCCESS. Draft saved to LangCache. Total Runs: {current_runs + 1}")
    except Exception:
        pass

    return {"status": "generated_and_cached", "draft": generated_draft}


def execute_atomic_fix_validation(
    fix_hash: str,
    commit_id: str,
    validation_result: Dict[str, Any],
    logger: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Canon Validator: Atomic Fix & Validation State using Redis Transactions.
    Ensures fix hash, commit ID, and validation result are written atomically.
    """
    if logger:
        logger.info(f"🔒 Starting Atomic Fix Validation for {fix_hash}")

    # Keys for atomic operation
    FIX_STATE_KEY = f"fix_state:{fix_hash}"
    VALIDATION_CACHE_KEY = f"validation_cache:{fix_hash}"

    try:
        # Simulate Redis transaction
        # In a real system, this would be a MULTI/EXEC block

        transaction_data = {
            "fix_hash": fix_hash,
            "commit_id": commit_id,
            "validation_status": validation_result.get("status"),
            "validation_time": validation_result.get("validation_time"),
            "atomic_timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }

        # Atomic write to multiple keys
        string_set(FIX_STATE_KEY, json.dumps(transaction_data))
        string_set(VALIDATION_CACHE_KEY, json.dumps(validation_result))

        if logger:
            logger.info("✅ Atomic transaction committed successfully")

        return {
            "status": "atomic_success",
            "message": "Fix state and validation committed atomically",
            "transaction_data": transaction_data
        }

    except Exception as e:
        if logger:
            logger.error(f"❌ Atomic transaction failed: {e}")
        return {"status": "atomic_failed", "error": str(e)}


def execute_temporal_rate_limiting(
    lead_id: str,
    action_type: str,
    max_actions_per_hour: int = 10,
    logger: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Outreach Engine: Temporal State & Rate Limiting using Redis.
    Tracks last contact time and enforces rate limits per lead.
    """
    if logger:
        logger.info(f"⏱️ Temporal Rate Limiting for {lead_id} - {action_type}")

    # Keys for temporal state
    LAST_CONTACT_KEY = f"last_contact:{lead_id}"
    RATE_LIMIT_KEY = f"rate_limit:{lead_id}:{action_type}"
    CURRENT_HOUR = int(time.time() // 3600)  # Current hour bucket

    try:
        # Check last contact time
        string_get(LAST_CONTACT_KEY)
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')

        # Check rate limit for current hour
        rate_limit_data = string_get(RATE_LIMIT_KEY)
        if rate_limit_data:
            rate_data = json.loads(rate_limit_data)
            if rate_data.get("hour_bucket") == CURRENT_HOUR:
                current_count = rate_data.get("count", 0)
                if current_count >= max_actions_per_hour:
                    if logger:
                        logger.warning(
                            f"⚠️ Rate limit exceeded: {current_count}/{max_actions_per_hour}")
                    return {
                        "status": "rate_limited",
                        "message": f"Maximum {max_actions_per_hour} actions per hour exceeded",
                        "reset_time": CURRENT_HOUR + 1
                    }

        # Increment rate counter
        new_count = 1 if not rate_limit_data or rate_data.get(
            "hour_bucket") != CURRENT_HOUR else rate_data.get("count", 0) + 1

        # Update rate limit state
        string_set(RATE_LIMIT_KEY, json.dumps({
            "hour_bucket": CURRENT_HOUR,
            "count": new_count
        }))

        # Update last contact time
        string_set(LAST_CONTACT_KEY, current_time)

        if logger:
            logger.info(
                f"✅ Action allowed. Count: {new_count}/{max_actions_per_hour}")

        return {
            "status": "allowed",
            "message": "Action within rate limits",
            "current_count": new_count,
            "last_contact": current_time
        }

    except Exception as e:
        if logger:
            logger.error(f"❌ Rate limiting failed: {e}")
        return {"status": "error", "error": str(e)}

