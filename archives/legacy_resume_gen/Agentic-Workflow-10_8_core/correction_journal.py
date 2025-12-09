from typing import Any, Dict

CORRECTION_JOURNAL = []


def record_correction_event(surface: str, recommendation: Dict[str, object], plan: Dict[str, object]):
    CORRECTION_JOURNAL.append(
        {
            "surface": surface,
            "recommendation": recommendation,
            "plan_objective": plan.get("objective"),
            "mode": plan.get("mode"),
        }
    )
