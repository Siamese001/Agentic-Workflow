from typing import Dict, Any


class ArbitrationEngine:
    """
    Deterministic stub arbitration engine.

    evaluate(state, qa_report, safety_patch) -> Dict[str,str]
    returns one of: accept, retry, replan, escalate
    """

    def evaluate(self, state: Dict[str, Any], qa_report: Dict[str, Any], safety_patch: Dict[str, Any]) -> Dict[str, str]:
        # 1) If safety is blocked → escalate
        sg = safety_patch.get("safety_gateway", {})
        if sg.get("status") == "blocked":
            return {"action": "escalate", "reason": "safety_blocked"}

        # 2) If QA findings are pending → retry
        findings = qa_report.get("findings", [])
        for f in findings:
            if f.get("status") == "pending":
                return {"action": "retry", "reason": "qa_pending"}

        # 3) If there are no messages at all → replan
        messages = state.get("messages", [])
        if not messages:
            return {"action": "replan", "reason": "no_messages"}

        # 4) Default: accept
        return {"action": "accept", "reason": "default_accept"}
