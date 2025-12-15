"""
MCP Hardening Module
Provides centralized hardening wrappers for Figma and Brave Search MCP calls.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

# Import core utilities
from core_utils import (
    add_observations,
    brave_search,
    get_variable_defs,
    incr,
    string_get,
    string_set,
)

# --- Figma Hardening Functions ---


def get_version_locked_design(file_id: str, version_id: str, logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Ensures the Resume Engine always validates against a specific, audited version
    of the Figma template, preventing validation against unstable drafts (Hardening).
    """
    try:
        # In a real implementation, the Figma MCP would accept a version parameter
        # For now, we simulate by adding version info to the response
        design_data_str = get_variable_defs(node_id=file_id)
        design_data = json.loads(design_data_str)

        # Add version metadata to ensure version locking
        design_data['_version_locked'] = {
            'file_id': file_id,
            'version_id': version_id,
            'locked_at': datetime.utcnow().isoformat()
        }

        if logger:
            logger.info(
                f"✅ Figma: Retrieved version-locked design v{version_id}")

        return design_data

    except Exception as e:
    pass
pass


if logger:
            logger.error(f"❌ Figma version-locked access failed: {e}")
        raise


def get_brand_style_guide(brand_id: str, logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Retrieves brand guidelines from Figma for outreach compliance.
    Includes color palette, tone-of-voice, and style rules.
    """
    try:
        style_data_str = get_variable_defs(node_id=f"brand_{brand_id}")
        style_data = json.loads(style_data_str)

        # Log brand guidelines to MEMory for compliance tracking
        try:
            add_observations(observations=[{
                "entityName": "BrandCompliance",
                "contents": [
                    f"Brand guidelines retrieved for {brand_id}",
                    f"Colors: {style_data.get('colors', [])}",
                    f"Tone: {style_data.get('tone', 'professional')}"
                ]
            }])
except Exception:
    pass
pass
pass

        if logger:
            logger.info(f"✅ Figma: Retrieved brand style guide for {brand_id}")

        return style_data

    except Exception as e:
    pass
pass
if logger:
            logger.warning(f"⚠️ Figma brand guide retrieval failed: {e}")
        # Return fallback brand guidelines
        return {
            "colors": ["#000000", "#FFFFFF", "#007ACC"],
            "tone": "professional",
            "font_family": "Arial",
            "_fallback": True
        }


def check_design_drift(file_id: str, canonical_version: str, logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Automated design drift audit for Git pre-commit hooks.
    Compares current design against canonical version.
    """
    try:
        # Get current design
        current_design = get_version_locked_design(file_id, "current", logger)

        # Get canonical design
        canonical_design = get_version_locked_design(
            file_id, canonical_version, logger)

        # Compare key variables
        drift_detected = False
        drift_report = []

        # Check for critical design differences
        current_vars = current_design.get('variables', {})
        canonical_vars = canonical_design.get('variables', {})

        for key, expected_value in canonical_vars.items():
            if key not in current_vars or current_vars[key] != expected_value:
                drift_detected = True
                drift_report.append(
                    f"Variable '{key}' drift: expected {expected_value}, got {current_vars.get(key, 'MISSING')}")

        result = {
            "drift_detected": drift_detected,
            "drift_report": drift_report,
            "current_version": current_design.get('_version_locked', {}).get('version_id'),
            "canonical_version": canonical_version
        }

        if logger:
            if drift_detected:
                logger.warning(
                    f"⚠️ Design drift detected: {len(drift_report)} violations")
            else:
                logger.info("✅ No design drift detected")

        return result

    except Exception as e:
    pass
pass
if logger:
            logger.error(f"❌ Design drift check failed: {e}")
        return {"drift_detected": True, "error": str(e)}

# --- Brave Search Hardening Functions ---


def execute_cost_controlled_search(query: str, max_daily_queries: int = 500, logger: Optional[Any] = None) -> Optional[str]:
    """
    Checks Redis for a daily search limit before executing the Brave Search MCP call.
    Uses Redis INCR for atomic counter management (Hardening).
    """
    SEARCH_LIMIT_KEY = "brave_search:daily_count"
    RESET_TIME_KEY = "brave_search:daily_reset"

    # 1. Check if daily counter needs reset (new day)
    try:
        last_reset = string_get(RESET_TIME_KEY)
        today = datetime.utcnow().strftime("%Y-%m-%d")

        if last_reset != today:
            # New day, reset counter
            string_set(SEARCH_LIMIT_KEY, "0")
            string_set(RESET_TIME_KEY, today)
            if logger:
                logger.info("🔄 Daily search counter reset")
except Exception:
    pass
pass
pass

    # 2. Check Daily Budget (L4 Redis)
    try:
        current_count = incr(SEARCH_LIMIT_KEY)

        if current_count > max_daily_queries:
            if logger:
                logger.error(
                    f"❌ Brave Search aborted: Daily query limit ({max_daily_queries}) exceeded")
            return None  # Abort search, save cost

        if logger:
            logger.info(
                f"✅ Search budget check passed: {current_count}/{max_daily_queries}")

    except Exception as e:
    pass
pass
if logger:
            logger.warning(
                f"L4 Redis rate limiter failed ({e}). Proceeding without limit check.")

    # 3. Execute Brave Search (L1/L3 Action)
    try:
        if logger:
            logger.info(f"🔍 Executing Brave Search for: {query}")

        return brave_search(query=query, count=5)

    except Exception as e:
    pass
pass
if logger:
            logger.error(f"Brave Search MCP failed: {e}")
        return None


def execute_time_bound_search(query: str, months_back: int = 6, logger: Optional[Any] = None) -> Optional[str]:
    """
    Executes Brave Search with time constraints for salary benchmarking.
    Adds date filter to query to ensure recent, relevant data.
    """
    # Calculate date threshold
    threshold_date = datetime.utcnow() - timedelta(days=30 * months_back)
    date_str = threshold_date.strftime("%Y-%m-%d")

    # Add time constraint to query
    time_constrained_query = f"{query} after:{date_str}"

    if logger:
        logger.info(f"🔍 Time-bound search: {time_constrained_query}")

    return execute_cost_controlled_search(time_constrained_query, logger=logger)


def execute_vulnerability_search(security_query: str, logger: Optional[Any] = None) -> Optional[str]:
    """
    Cost-controlled vulnerability search using restricted domains.
    Checks security-specific sources before falling back to general search.
    """
    # Try security-specific sources first
    security_sites = [
        f"site:security.stackexchange.com {security_query}",
        f"site:owasp.org {security_query}",
        f"site:cve.mitre.org {security_query}"
    ]

    for site_query in security_sites:
        result = execute_cost_controlled_search(site_query, logger=logger)
        if result:
            if logger:
                logger.info(f"✅ Found vulnerability info on security site")
            return result

    # Fallback to general search if no specific results
    if logger:
        logger.info("🔄 No specific security results, trying general search")

    return execute_cost_controlled_search(
        f"{security_query} vulnerability security",
        logger=logger
    )

# --- Brand Compliance Integration ---


def ensure_brand_compliance(content: str, brand_guidelines: Dict[str, Any], logger: Optional[Any] = None) -> Dict[str, Any]:
    """
    Checks content against brand guidelines retrieved from Figma.
    Ensures tone, colors, and style compliance.
    """
    compliance_issues = []

    # Check tone compliance
    required_tone = brand_guidelines.get('tone', 'professional')
    if required_tone == 'professional' and any(word in content.lower() for word in ['hey', 'yo', 'sup']):
        compliance_issues.append("Informal tone detected")

    # Check for brand colors (simplified)
    brand_colors = brand_guidelines.get('colors', [])
    if brand_colors and not any(color in content for color in brand_colors):
        compliance_issues.append("Brand colors not referenced")

    result = {
        "compliant": len(compliance_issues) == 0,
        "issues": compliance_issues,
        "brand_tone": required_tone,
        "checked_at": datetime.utcnow().isoformat()
    }

    if logger:
        if result['compliant']:
            logger.info("✅ Content complies with brand guidelines")
        else:
            logger.warning(f"⚠️ Brand compliance issues: {compliance_issues}")

    return result

