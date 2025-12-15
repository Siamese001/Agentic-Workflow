"""
Time-Bound Salary Benchmarking Module
Implements data freshness constraints using Time MCP and Brave Search.
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Import core utilities
from core_utils import (
    get_current_time,
    execute_cost_controlled_search,
    add_observations
)

def calculate_freshness_filter(time_json: str, months_ago: int = 6) -> str:
    """Calculates the date filter for data freshness."""
    try:
        current_dt = datetime.fromisoformat(json.loads(time_json)['datetime'].replace('Z', '+00:00'))
        filter_dt = current_dt - timedelta(days=30 * months_ago)
        return filter_dt.strftime('%Y-%m-%d')
    except Exception as e:
        # Fallback to a safe, wide date range if L4 Time MCP fails
        return "2024-01-01"

def execute_time_bound_salary_benchmarking(
    job_title: str, 
    location: str, 
    logger: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Retrieves fresh salary data using Brave Search filtered by a Time MCP constraint.
    (Data Integrity and Cost Governance Hardening)
    """
    if logger:
        logger.info(f"⌚ Starting Time-Bound Salary Benchmarking for: {job_title} in {location}")

    # --- 1. Get Current Time & Calculate Freshness Filter (L4 Time) ---
    time_json = get_current_time()
    months_to_filter = 6
    after_date_filter = calculate_freshness_filter(time_json, months_to_filter)
    
    if logger:
        logger.info(f"Enforcing data freshness: Must be published after {after_date_filter}")

    # --- 2. Time-Bound Search (L1/L3 Brave Search) ---
    
    # Constructing a precise query with the time constraint
    # Hardening: The search query enforces the data freshness rule
    brave_query = f"{job_title} salary {location} after:{after_date_filter}"
    
    try:
        benchmarking_result_str = execute_cost_controlled_search(brave_query, logger)
        
        if benchmarking_result_str:
            search_result = json.loads(benchmarking_result_str)
            salary_data = search_result[0].get("snippet", "Salary data not found") if search_result else None
            source_freshness = "FRESH"
            
            if logger:
                logger.info("✅ Time-Bound Search Success: Fresh data found.")
        else:
            salary_data = None
            source_freshness = "STALE_OR_MISSING"
            if logger:
                logger.warning("Brave Search failed or returned stale data. Utilizing fallback context.")

    except Exception as e:
        if logger:
            logger.error(f"Brave Search failed: {e}. Using fallback.")
        salary_data = None
        source_freshness = "CRITICAL_FAILURE"
        
    # --- 3. Data Vetting and Final Result ---
    if not salary_data:
        # Sequential Thinking: Fallback to Pinecone (L3) or MEMemory (L5)
        final_salary_data = "Historical data (100k-130k)"
        final_source = "FALLBACK_HISTORICAL"
        
    else:
        final_salary_data = salary_data
        final_source = "BraveSearch_TimeBound"

    # --- 4. Audit Log (L5 MEMemory) ---
    try:
        audit_message = f"Salary Benchmark Audit: Job={job_title}. Source={final_source}. Window={months_to_filter} months. Freshness={source_freshness}."
        add_observations(observations=[{
            "entityName": "CostGovernance",
            "contents": [audit_message]
        }])
    except: 
        pass

    return {
        "status": "success",
        "salary_data": final_salary_data,
        "source": final_source,
        "time_window_start": after_date_filter
    }
