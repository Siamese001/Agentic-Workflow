from __future__ import annotations
from dataclasses import dataclass
"""
SemanticDebuggerAgent — L5 Safety Agent for Just-In-Time RCA

Analyzes runtime errors using the Semantic Knowledge Base (Pinecone)
to find known healing patterns and fixes.
"""
from typing import Dict, Any, List
import logging

from agentic_core.L5_safety.guardrails.L5SafetyBaseAgent import L5SafetyBaseAgent
from agentic_core.utils.core_extensions.CognitiveRecoveryMixin import CognitiveRecoveryMixin
from agentic_core.L3_orchestration.mixins.L3SubatomicTestingMixin import SubatomicTestingMixin

Logger = logging.getLogger(__name__)


@dataclass
class SemanticDebuggerAgent(SubatomicTestingMixin, L5SafetyBaseAgent, CognitiveRecoveryMixin):
    """
    L5 Safety Agent responsible for performing Just-In-Time Root Cause Analysis (RCA).

    It utilizes the CognitiveRecoveryMixin to query the Semantic Knowledge Base (Pinecone)
    for known healing patterns matching incoming error traces.
    """

    def __init__(self, project_root=None, ctx=None, **kwargs) -> None:
        """Initialize the instance."""
        super().__init__(project_root=project_root, ctx=ctx, **kwargs)
        self.name = "SemanticDebuggerAgent"
        self.layer = "L5"
        self.description = "Analyzes runtime errors using semantic memory to find known fixes."

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method.

        Expected payload:
        {
            "error_message": str,
            "stack_trace": str,
            "context": str (optional)
        }
        """
        Logger.info("Starting Semantic Debugging Session...")

        error_msg = payload.get("error_message", "Unknown Error")
        stack_trace = payload.get("stack_trace", "")

        # 1. Synthesize the query for the brain
        query_context = f"{error_msg}\n{stack_trace}"

        # 2. Consult the Knowledge Base (Direct Pattern Search)
        patterns = self._find_healing_patterns(query_context)

        # 3. Analyze Results
        if patterns:
            best_fix = patterns[0]
            confidence = best_fix.score

            if confidence > 0.82:
                Logger.info(f"High confidence fix found: {best_fix.id} ({confidence:.2f})")
                return {
                    "status": "success",
                    "diagnosis": "Known Issue Identified",
                    "fix_proposal": best_fix.content,
                    "reference_doc": best_fix.metadata.get("source", "N/A"),
                    "confidence": confidence,
                }
            else:
                Logger.warning(f"Low confidence matches only. Top: {confidence:.2f}")
                return {
                    "status": "uncertain",
                    "diagnosis": "Novel Issue (Low Confidence Matches)",
                    "related_patterns": [p.id for p in patterns[:3]],
                    "confidence": confidence,
                }

        # 4. Fallback: Search Architecture Docs if no pattern found
        docs = self.consult_knowledge_base(
            f"Architecture handling for: {error_msg}", namespace="architecture-docs"
        )

        return {
            "status": "failed",
            "diagnosis": "No matching healing patterns found.",
            "suggested_reading": [d["id"] for d in docs] if docs else [],
        }

    def _find_healing_patterns(self, error_context: str) -> List:
        """Wrapper around the Mixin's client to search healing namespace directly."""
        client = self._get_cognitive_client()
        return client.find_healing_pattern(error_context)

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> Dict[str, Any]:
        """Autonomous healing with proper invocation chain."""
        super().heal_repository(dry_run=dry_run, execute=execute, **kwargs)
        return {"violations": 0, "fixed": 0, "errors": 0}
