"""
SelfDiagnosisMixin – Agents that monitor their own health
"""
from typing import Dict, List, Any


class SelfDiagnosisMixin:
    MANDATORY_COMPONENTS: List[str] = []

    async def self_diagnose(self) -> Dict[str, Any]:
        diagnosis = {"health": "healthy", "issues": [], "self_repairs": []}

        for component_name in self.MANDATORY_COMPONENTS:
            component = getattr(self, component_name, None)
            if not component:
                diagnosis["issues"].append({"type": "missing_component", "name": component_name})
                continue

            try:
                health = await component.health_check() if hasattr(component, "health_check") else {"healthy": True}
                if not health.get("healthy"):
                    diagnosis["issues"].append({"component": component_name, "issue": health.get("issue")})
            except Exception as e:
                diagnosis["issues"].append({"component": component_name, "error": str(e)})

        diagnosis["health"] = "healthy" if not diagnosis["issues"] else "degraded"
        return diagnosis
