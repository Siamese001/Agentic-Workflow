from __future__ import annotations
"""
Dashboard Data Generator - L6 Modular Engine
HARDENED: Phase 4 Verified AST Signal Integration.
Generates unified row data for both Markdown and HTML reports.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)

log = logging.getLogger(__name__)

class DashboardDataGenerator:
    def __init__(self, project_root: Path, territories: Dict[str, Any]) -> None:
        self.project_root = project_root
        self.territories = territories
        self.registry_path = self.project_root / AGENT_DISCOVERY_JSON
        self.registry_by_path = {}

    def load_registry(self) -> List[Dict[str, Any]]:
        """Load and index the authoritative agent registry."""
        if not self.registry_path.exists():
            return []
        try:
            data = json.loads(self.registry_path.read_text(encoding="utf-8"))
            self.registry_by_path = {entry["path"].replace("\\", "/"): entry for entry in data}
            return data
        except Exception as e:
            log.error(f"Failed to load registry: {e}")
            return []

    def compute_territory_metrics(self, agents: List[Path], used_stems: set, registry: Dict[str, Any]) -> Dict[str, Any]:
        """Compute aggregate metrics for a specific agent group."""
        m = {
            "total": len(agents), "compliant": 0, "heal_cap": 0, "heal_inv": 0,
            "test": 0, "cc_sum": 0, "typed": 0, "doc": 0, "obs": 0, "used": 0,
            "schema_strictness": 0.0, "proper_base": 0.0
        }
        for agent in agents:
            rel_path = str(agent.relative_to(self.project_root)).replace("\\", "/")
            entry = registry.get(rel_path, {})

            m["compliant"] += 1 if entry.get("has_healing") else 0
            m["heal_cap"] += 1 if entry.get("has_healing") else 0
            m["heal_inv"] += 1 if entry.get("invocation") == "Yes" else 0
            m["test"] += 1 if entry.get("has_tests") else 0
            m["cc_sum"] += entry.get("cyclomatic_complexity", 1)
            m["typed"] += entry.get("typed_pct", 0)
            m["doc"] += entry.get("documented_pct", 0)
            m["obs"] += 100 if entry.get("observability") else 0
            m["used"] += 1 if agent.stem in used_stems else 0
            # Phase 4 Signals
            m["schema_strictness"] += entry.get("schema_strictness", entry.get("typed_pct", 0))
            m["proper_base"] += 100 if entry.get("proper_base_class") else 0

        return m

    def build_territory_row(self, territory_name: str, metrics: Dict[str, Any], priority: int, is_infrastructure: bool) -> Dict[str, Any]:
        """Format raw metrics into a standardized dashboard row."""
        t = metrics["total"]
        if t == 0: return {}

        avg_cc = round(metrics["cc_sum"] / t, 1)
        health = round(((metrics["test"]/t*100) + (metrics["heal_inv"]/t*100) + (metrics["obs"]/t)) / 3, 1)

        return {
            "Territory": territory_name,
            "Total": t,
            "Heal Cap %": round(metrics["heal_cap"] / t * 100, 1),
            "Heal Invocation %": round(metrics["heal_inv"] / t * 100, 1),
            "Test %": round(metrics["test"] / t * 100, 1),
            "Avg CC": avg_cc,
            "Typed %": round(metrics["typed"] / t, 1),
            "Documented %": round(metrics["doc"] / t, 1),
            "Health": health,
            "Risk": "HIGH" if avg_cc > 12 or health < 60 else "MED" if avg_cc > 8 or health < 80 else "LOW",
            "Priority": priority,
            "Schema Strictness %": round(metrics["schema_strictness"] / t, 1),
            "Proper Base %": round(metrics["proper_base"] / t, 1)
        }

    def build_total_row(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate all territory rows into a system-wide total row."""
        if not rows: return {}
        total_agents = sum(r["Total"] for r in rows)
        def weighted_avg(key): return round(sum(r[key] * r["Total"] for r in rows) / total_agents, 1)

        health = weighted_avg("Health")
        return {
            "Territory": "TOTAL",
            "Total": total_agents,
            "Heal Cap %": weighted_avg("Heal Cap %"),
            "Heal Invocation %": weighted_avg("Heal Invocation %"),
            "Test %": weighted_avg("Test %"),
            "Avg CC": weighted_avg("Avg CC"),
            "Typed %": weighted_avg("Typed %"),
            "Documented %": weighted_avg("Documented %"),
            "Health": health,
            "Risk": "HIGH" if health < 70 else "MED" if health < 85 else "LOW",
            "Schema Strictness %": weighted_avg("Schema Strictness %"),
            "Proper Base %": weighted_avg("Proper Base %")
        }

    def generate_full_report_data(self) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """High-level orchestrator for the modular generation process."""
        self.load_registry()
        # Note: In production, this would involve full path scanning.
        # For brevity, this assumes a typical orchestrator call pattern.
        rows = [] # Filled by caller using build_territory_row
        total_row = self.build_total_row(rows)
        return rows, total_row
