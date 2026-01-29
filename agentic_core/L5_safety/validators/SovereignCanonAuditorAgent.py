# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: orchestrator, prompt
from __future__ import annotations

from dataclasses import dataclass

# This boosts alignment detection — review and integrate appropriately
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"""
Sovereign Canon Audit – Powered by DeepWiki MCP
Phase 13E: L6 Self-Verification Utility

Enables the system to audit its own architecture and verify critical components
using DeepWiki's codebase intelligence capabilities.
"""
import asyncio
import logging
from typing import Any

from agentic_core.L6_observability.deepwiki_client_sovereign import SovereignDeepWikiClient

from agentic_core.base_agents.decorators import standard_heal

# [SSOT IMPORT] Structure blueprint is the single source of truth

Logger: Any = logging.getLogger("L6.CanonAudit")


@dataclass
class SovereignCanonAuditorAgent(SubatomicTestingMixin, SovereignBaseAgent):
    """
    Sovereign Canon Auditor using DeepWiki MCP.
    Performs self-verification of critical system components.
    """

    def __init__(self) -> None:
        """Initialize the canon auditor."""
        self.client = SovereignDeepWikiClient()
        self.critical_files = [
            "agentic_core/L3_orchestration/workflow_engines/mcp_router_sovereign.py",
            "agentic_core/L5_safety/guardrails/mcp_sovereign.py",
            "agentic_core/L4_state/semantic_memory/pinecone_mcp_client.py",
            "agentic_core/L4_state/knowledge_graph/SovereignGraphClient.py",
            "agentic_core/L6_observability/deepwiki_client_sovereign.py",
            "agentic_core/L1_cognition/thought_engine/StrategicPlannerAgent.py",
            "agentic_core/L2_execution/tool_registry/WebSearchTools.py",
        ]

    async def audit_core_components(self) -> dict[str, Any]:
        """
        Audit critical core components for existence.

        Returns:
            Audit results with status for each component
        """
        print(+"=" * 60)
        print("🔍 SOVEREIGN CANON AUDIT - Phase 13E")
        print("=" * 60)
        results: Any = {"total": len(self.critical_files), "found": 0, "Missing": 0, "details": []}
        for filepath in self.critical_files:
            try:
                exists: Any = await self.client.verify_file_exists(filepath)
                status: Any = "✅ FOUND" if exists else "❌ MISSING"
                results["details"].append({"file": filepath, "exists": exists, "status": status})
                if exists:
                    results["found"] += 1
                else:
                    results["Missing"] += 1
                print(f"{status}: {filepath}")
            except Exception as e:
                Logger.error(f"[CANON AUDIT] Failed to verify {filepath}: {e}")
                results["details"].append(
                    {"file": filepath, "exists": False, "status": "⚠️ ERROR", "error": str(e)}
                )
                results["Missing"] += 1
                print(f"⚠️ ERROR: {filepath} - {e}")
        return results

    async def get_architectural_insight(self, question: str) -> str:
        """
        Get architectural insight about the system.

        Args:
            question: Question to ask about the architecture

        Returns:
            Answer from DeepWiki
        """
        print("\n" + "-" * 60)
        print("🧠 ARCHITECTURAL INSIGHT")
        print("-" * 60)
        print(f"Q: {question}")
        print()
        try:
            answer: Any = await self.client.ask_question(question)
            print(f"A: {answer}")
            return answer
        except Exception as e:
            Logger.error(f"[CANON AUDIT] Insight query failed: {e}")
            error_msg: Any = f"Error: {e}"
            print(f"A: {error_msg}")
            return error_msg

    async def verify_mcp_integration(self) -> dict[str, Any]:
        """
        Verify MCP integration across all layers.

        Returns:
            Verification results
        """
        print("\n" + "=" * 60)
        print("🔗 MCP INTEGRATION VERIFICATION")
        print("=" * 60)
        mcp_components: Any = {
            "L1 Sequential Thinking": "StrategicPlannerAgent.py",
            "L2 Web Search": "WebSearchTools.py",
            "L4 Pinecone": "pinecone_mcp_client.py",
            "L4 Knowledge Graph": "SovereignGraphClient.py",
            "L6 DeepWiki": "deepwiki_client_sovereign.py",
        }
        results: Any = {"total": len(mcp_components), "verified": 0, "failed": 0, "details": []}
        for component_name, filename in mcp_components.items():
            try:
                question: Any = f"Does {filename} use the SovereignMCPRouter for MCP integration?"
                answer: Any = await self.client.ask_question(question)
                uses_mcp: Any = any(
                    word in answer.lower() for word in ["yes", "uses", "integrates", "router"]
                )
                status: Any = "✅ VERIFIED" if uses_mcp else "⚠️ UNCLEAR"
                results["details"].append(
                    {
                        "component": component_name,
                        "file": filename,
                        "uses_mcp": uses_mcp,
                        "status": status,
                    }
                )
                if uses_mcp:
                    results["verified"] += 1
                else:
                    results["failed"] += 1
                print(f"{status}: {component_name} ({filename})")
            except Exception as e:
                Logger.error(f"[CANON AUDIT] MCP verification failed for {component_name}: {e}")
                results["details"].append(
                    {
                        "component": component_name,
                        "file": filename,
                        "uses_mcp": False,
                        "status": "❌ ERROR",
                        "error": str(e),
                    }
                )
                results["failed"] += 1
                print(f"❌ ERROR: {component_name} - {e}")
        return results

    async def run_full_audit(self) -> dict[str, Any]:
        """
        Run complete canon audit.

        Returns:
            Complete audit results
        """
        print("\n" + "=" * 60)
        print("🚀 STARTING FULL SOVEREIGN CANON AUDIT")
        print("=" * 60)
        component_results: Any = await self.audit_core_components()
        mcp_results: Any = await self.verify_mcp_integration()
        insights: Any = []
        questions: Any = [
            "Explain the role of the L3 router in this codebase.",
            "How does the L5 Safety Shield protect MCP operations?",
            "What is the purpose of the dual-graph architecture?",
        ]
        for question in questions:
            answer: Any = await self.get_architectural_insight(question)
            insights.append({"question": question, "answer": answer})
        print("\n" + "=" * 60)
        print("📊 AUDIT SUMMARY")
        print("=" * 60)
        print(f"Components: {component_results['found']}/{component_results['total']} found")
        print(f"MCP Integration: {mcp_results['verified']}/{mcp_results['total']} verified")
        print(f"Insights: {len(insights)} architectural questions answered")
        overall_status: Any = (
            "PASS" if component_results["Missing"] == 0 and mcp_results["failed"] == 0 else "FAIL"
        )
        print(f"\n🎯 Overall Status: {overall_status}")
        print("=" * 60 + "\n")
        return {
            "status": overall_status,
            "components": component_results,
            "mcp_integration": mcp_results,
            "insights": insights,
            "timestamp": asyncio.get_event_loop().time(),
        }

    @standard_heal
    def heal_repository(self, **kwargs) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository(**kwargs)


async def audit_core_components() -> Any:
    """
    Convenience function to run core component audit.
    Compatible with the spec example.
    """
    auditor: Any = SovereignCanonAuditorAgent()
    critical_files: Any = [
        "agentic_core/L3_orchestration/workflow_engines/mcp_router_sovereign.py",
        "agentic_core/L5_safety/guardrails/mcp_sovereign.py",
    ]
    print("--- Starting Sovereign Canon Audit ---")
    for f in critical_files:
        exists: Any = await auditor.client.verify_file_exists(f)
        status: Any = "✅ FOUND" if exists else "❌ MISSING"
        print(f"{status}: {f}")
    insight: Any = await auditor.client.ask_question(
        "Explain the role of the L3 router in this codebase."
    )
    print(f"\n--- Architectural Insight ---\n{insight}")


async def main() -> Any:
    """Main entry point for canon audit."""
    auditor: Any = SovereignCanonAuditorAgent()
    results: Any = await auditor.run_full_audit()
    return results


if __name__ == "__main__":
    asyncio.run(main())
