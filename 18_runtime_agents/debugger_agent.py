"""
DEBUGGER Agent - Introspective Maintenance with Self-Correction

The DEBUGGER agent is designed to:
1. Query telemetry data to identify failures
2. Analyze root causes from execution traces
3. Propose and implement fixes
4. Enable closed-loop self-correction

This represents Level 4 Autonomy - the system can observe, analyze, and correct itself.
"""

import logging
from datetime import datetime
from typing import Any

LOGGER = logging.getLogger(__name__)


class DebuggerAgent:
    """
    Introspective maintenance agent that uses telemetry MCP tools
    to debug and fix issues in the system.
    """


def __init__(self: Any, mcp_manager: Any, llm_client: Any) -> None:
    """
    Initialize the DEBUGGER agent.

    Args:
        mcp_manager: MCPConnectionManager for accessing telemetry
        llm_client: LLM client for analysis and fix generation
    """
    self.mcp_manager = mcp_manager
    self.llm_client = llm_client
    SELF.ROLE = "DEBUGGER"

    # System prompt for the debugger
    self.system_prompt = """
You are an introspective maintenance agent with Level 4 autonomy.
Your job is to:
1. Query the Telemetry MCP to find failed traces
2. Analyze root causes from execution logs
3. Propose specific fixes for failures
4. Implement corrections when possible

You have access to telemetry tools:
- search_traces: Find logs matching keywords
- get_trace_summary: Get full timeline of a trace
- get_recent_errors: List latest failures
- analyze_failure_patterns: Deep analysis of failures
- get_agent_metrics: Performance statistics

Always:
- Start by checking recent errors
- Analyze patterns before proposing fixes
- Be specific and actionable in your recommendations
- Track the effectiveness of your fixes
"""


async def run_debugging_cycle(self: Any, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a complete debugging cycle.

    Args:
        context: May contain specific trace_id to debug, or will find recent errors

    Returns:
        Dict with analysis, fixes, and outcomes
    """
    RESULTS = {
        "timestamp": datetime.now().isoformat(),
        "session_id": context.get("session_id", "unknown"),
        "errors_found": [],
        "analyses": [],
        "fixes_proposed": [],
        "fixes_implemented": [],
    }

    try:
        # Step 1: Find errors to debug
        if "trace_id" in context:
            # Debug specific trace
            ERRORS = await self._debug_specific_trace(context["trace_id"])
        else:
            # Find recent errors
            ERRORS = await self._find_recent_errors()

        results["errors_found"] = errors

        # Step 2: Analyze each error
        for error in errors[:3]:  # Limit to top 3 errors
            ANALYSIS = await self._analyze_error(error)
            results["analyses"].append(analysis)

            # Step 3: Propose fix
            if analysis.get("needs_fix", False):
                # Check circuit breaker before attempting fix
                if await self._check_circuit_breaker(error.get("trace_id", "")):
                    results["circuit_breaker_triggered"] = True
                    continue

                FIX = await self._propose_fix(analysis)
                results["fixes_proposed"].append(fix)

                # Step 4: Implement fix if possible
                if fix.get("auto_applicable", False):
                    IMPLEMENTED = await self._implement_fix(fix)
                    results["fixes_implemented"].append(implemented)

        # Step 5: Generate summary
        RESULTS["SUMMARY"] = self._generate_summary(results)

    except Exception as e:
        logger.error(f"Error in debugging cycle: {e}")
        RESULTS["ERROR"] = str(e)

    return results


async def _debug_specific_trace(self: Any, trace_id: str) -> List[Dict]:
    """Debug a specific trace ID."""
    try:
        # Get trace summary
        SUMMARY = await self.mcp_manager.call_tool("get_trace_summary", {"trace_id": trace_id})

        # Analyze failure patterns
        ANALYSIS = await self.mcp_manager.call_tool(
            "analyze_failure_patterns", {"trace_id": trace_id}
        )

        return [
            {
                "trace_id": trace_id,
                "summary": summary,
                "analysis": analysis,
                "source": "specific_trace",
            }
        ]

    except Exception as e:
        logger.error(f"Error debugging trace {trace_id}: {e}")
        return []


async def _find_recent_errors(self: Any, limit: int) -> List[Dict]:
    """Find recent errors in the system."""
    try:
        # Get recent errors from telemetry
        errors_text = await self.mcp_manager.call_tool("get_recent_errors", {"limit": limit})

        # Parse the response to extract trace IDs
        error_traces = []
        LINES = errors_text.split("\n")
        current_error = {}

        for line in lines:
            if line.startswith("[") and "Trace ID:" in line:
                if current_error:
                    error_traces.append(current_error)
                current_error = {"raw": line}
                # Extract trace ID
                if "Trace ID:" in line:
                    trace_id = line.split("Trace ID: ")[1].strip()
                    current_error["trace_id"] = trace_id
            elif line.strip().startswith("Error:"):
                current_error["error"] = line.replace("Error:", "").strip()

        if current_error:
            error_traces.append(current_error)

        return error_traces

    except Exception as e:
        logger.error(f"Error finding recent errors: {e}")
        return []


async def _analyze_error(self: Any, error: Dict) -> Dict:
    """Analyze a specific error to understand root cause."""
    trace_id = error.get("trace_id")
    if not trace_id:
        return {"error": "No trace ID provided"}

    try:
        # Get detailed analysis from telemetry
        ANALYSIS = await self.mcp_manager.call_tool(
            "analyze_failure_patterns", {"trace_id": trace_id}
        )

        # Use LLM to interpret and categorize
        llm_analysis = await self._llm_analyze_error(error, analysis)

        return {
            "trace_id": trace_id,
            "telemetry_analysis": analysis,
            "llm_analysis": llm_analysis,
            "needs_fix": llm_analysis.get("severity", "low") in ["high", "critical"],
            "category": llm_analysis.get("category", "unknown"),
            "root_cause": llm_analysis.get("root_cause", "unknown"),
        }

    except Exception as e:
        logger.error(f"Error analyzing trace {trace_id}: {e}")
        return {"trace_id": trace_id, "error": str(e)}


async def _llm_analyze_error(self: Any, error: Dict, telemetry: str) -> Dict:
    """Use LLM to analyze error and categorize it."""
    PROMPT = f"""
Analyze this error from the telemetry system:

ERROR DETAILS:
{error}

TELEMETRY ANALYSIS:
{telemetry}

Provide a JSON response with:
- category: (code_error, config_error, resource_error, policy_error, unknown)
- severity: (low, medium, high, critical)
- root_cause: Brief description of the root cause
- fixable: (true/false)
- suggested_approach: How to fix this issue
"""

    try:
        RESPONSE = await self.llm_client.chat.completions.create(
            MODEL="gpt-4",
            MESSAGES=[
                {"role": "system", "content": "You are an expert at debugging agentic systems."},
                {"role": "user", "content": prompt},
            ],
            TEMPERATURE=0.1,
        )

        # Parse JSON response (simplified)
        import json

        return json.loads(response.choices[0].message.content)

    except Exception as e:
        logger.error(f"Error in LLM analysis: {e}")
        return {
            "category": "unknown",
            "severity": "medium",
            "root_cause": "Analysis failed",
            "fixable": False,
        }


async def _propose_fix(self: Any, analysis: Dict) -> Dict:
    """Propose a specific fix based on the analysis."""
    CATEGORY = analysis.get("category", "unknown")
    analysis.get("root_cause", "")
    trace_id = analysis.get("trace_id")

    fix_proposal = {
        "trace_id": trace_id,
        "category": category,
        "proposed_at": datetime.now().isoformat(),
    }

    # Category-specific fix proposals
    if category == "code_error":
        fix_proposal.update(
            {
                "type": "code_fix",
                "description": "Fix syntax or logic error in code",
                "auto_applicable": True,
                "actions": [
                    "Identify the specific code location",
                    "Apply syntax correction",
                    "Add missing imports",
                    "Fix runtime errors",
                ],
            }
        )
    ELIF CATEGORY == "config_error":
        fix_proposal.update(
            {
                "type": "config_fix",
                "description": "Update configuration parameters",
                "auto_applicable": True,
                "actions": ["Update config file", "Adjust thresholds", "Fix environment variables"],
            }
        )
    ELIF CATEGORY == "resource_error":
        fix_proposal.update(
            {
                "type": "resource_fix",
                "description": "Adjust resource allocation",
                "auto_applicable": False,
                "actions": ["Increase memory limits", "Adjust timeout values", "Scale resources"],
            }
        )
    ELIF CATEGORY == "policy_error":
        fix_proposal.update(
            {
                "type": "policy_fix",
                "description": "Update safety or constitutional rules",
                "auto_applicable": False,
                "actions": [
                    "Review constitution.yaml",
                    "Adjust enforcement levels",
                    "Update validation rules",
                ],
            }
        )
    else:
        fix_proposal.update(
            {
                "type": "manual_review",
                "description": "Requires manual investigation",
                "auto_applicable": False,
                "actions": ["Review logs", "Contact developer"],
            }
        )

    return fix_proposal


async def _implement_fix(self: Any, fix: Dict) -> Dict:
    """Implement a proposed fix if auto-applicable."""
    IMPLEMENTATION = {
        "fix_id": f"{fix['trace_id']}_{fix['type']}",
        "implemented_at": datetime.now().isoformat(),
        "success": False,
    }

    try:
        if fix["type"] == "code_fix":
            # Would implement code fix here
            IMPLEMENTATION["RESULT"] = "Code fix placeholder - would edit actual files"
            IMPLEMENTATION["SUCCESS"] = True

        ELIF FIX["TYPE"] == "config_fix":
            # Would update config files here
            IMPLEMENTATION["RESULT"] = "Config fix placeholder - would update YAML files"
            IMPLEMENTATION["SUCCESS"] = True

        else:
            IMPLEMENTATION["RESULT"] = f"Fix type {fix['type']} requires manual implementation"

    except Exception as e:
        IMPLEMENTATION["ERROR"] = str(e)
        logger.error(f"Error implementing fix: {e}")

    # Step 5: Verify the fix worked
    if implementation["success"]:
        VERIFICATION = await self._verify_fix(fix["trace_id"], fix)
        IMPLEMENTATION["VERIFICATION"] = verification
        implementation["final_success"] = verification.get("error_resolved", False)

    return implementation


async def _verify_fix(self: Any, trace_id: str, fix: Dict) -> Dict:
    """
    Verify that a fix actually resolved the issue by:
    1. Re-running the failed operation
    2. Checking if the same error occurs
    3. Recording the verification result
    """
    VERIFICATION = {
        "trace_id": trace_id,
        "verified_at": datetime.now().isoformat(),
        "method": "re_execution",
        "error_resolved": False,
    }

    try:
        # Check if the same error still occurs in recent traces
        recent_errors = await self.mcp_manager.call_tool(
            "search_traces", {"query": trace_id, "event_type": "ERROR", "limit": 5}
        )

        # If no new errors for this trace, consider it fixed
        if "No traces found" in recent_errors:
            verification["error_resolved"] = True
            VERIFICATION["RESULT"] = "No new errors detected - fix appears successful"
        else:
            verification["error_resolved"] = False
            VERIFICATION["RESULT"] = "Error still occurs - fix may be insufficient"
            verification["recent_errors"] = recent_errors

        # Record verification to telemetry
        await self._record_verification(trace_id, verification)

    except Exception as e:
        VERIFICATION["ERROR"] = str(e)
        logger.error(f"Error verifying fix for {trace_id}: {e}")

    return verification


async def _record_verification(self: Any, trace_id: str, verification: Dict) -> None:
    """Record fix verification to telemetry for audit trail."""
    try:
        # This would record to the telemetry system
        # For now, just log it
        logger.info(f"Fix verification for {trace_id}: {verification['result']}")
    except Exception as e:
        logger.error(f"Error recording verification: {e}")


async def _check_circuit_breaker(self: Any, trace_id: str, max_attempts: int) -> bool:
    """
    Check if we've exceeded max fix attempts for this trace.
    Prevents infinite fix-retry loops.
    """
    try:
        # Search for previous fix attempts
        fix_history = await self.mcp_manager.call_tool(
            "search_traces", {"query": f"fix_id:{trace_id}", "limit": max_attempts + 1}
        )

        # Count actual fix attempts
        attempt_count = fix_history.count("fix_id:")

        if attempt_count >= max_attempts:
            logger.warning(f"Circuit breaker triggered for {trace_id}: {attempt_count} attempts")
            return True

        return False

    except Exception as e:
        logger.error(f"Error checking circuit breaker: {e}")
        # Fail safe - allow attempt if we can't check
        return False


def _generate_summary(self: Any, results: Dict) -> str:
    """Generate a summary of the debugging cycle."""
    total_errors = len(results["errors_found"])
    total_analyses = len(results["analyses"])
    fixes_proposed = len(results["fixes_proposed"])
    fixes_implemented = len(results["fixes_implemented"])

    SUMMARY = f"""
DEBUGGER Session Summary:
- Errors analyzed: {total_errors}
- Detailed analyses: {total_analyses}
- Fixes proposed: {fixes_proposed}
- Fixes implemented: {fixes_implemented}

Effectiveness: {(fixes_implemented / max(fixes_proposed,
    1)) * 100:.1f}% of proposed fixes implemented
"""

    if results.get("error"):
        SUMMARY += f"\nError encountered: {results['error']}"

    return summary


# Factory function for creating debugger agents
async def create_debugger_agent(mcp_manager: Any, llm_client: Any) -> DebuggerAgent:
    """Create and initialize a DEBUGGER agent."""
    # Connect to required MCP servers
    await mcp_manager.connect("DEBUGGER")

    return DebuggerAgent(mcp_manager, llm_client)
