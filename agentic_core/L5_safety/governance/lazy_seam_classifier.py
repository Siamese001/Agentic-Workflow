from agentic_core.L2_execution.tools import write_gateway as _wg

"""
Lazy Seam Allowlist Reason Classifier - Phase 4.2

Classifies lazy seams into reason categories based on their imports and context.
"""

import json
from pathlib import Path
from typing import Any
from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)


class LazySeamClassifier:
    """Classifies lazy seams into reason categories."""

    # Reason taxonomy from Phase 4.1
    REASON_TAXONOMY = {
        "D1_EXTERNAL_OPTIONAL_DEP": "Optional external dependencies (pinecone/redis/etc.)",
        "D2_ENTRYPOINT_SCRIPT": "CLI/scripts that orchestrate",
        "D3_PLUGIN_REGISTRY_DISPATCH": "Registry/dynamic dispatch boundaries",
        "D4_OBSERVABILITY_INTEGRATION": "Telemetry/probes integration",
        "D5_SECURITY_SAFETY_ADAPTER": "Policy adapters (boundary-only)",
    }

    def __init__(self, allowlist_path: Path):
        self.allowlist_path = allowlist_path
        self.allowlist_data = self._load_allowlist()

    def _load_allowlist(self) -> dict[str, Any]:
        """Load allowlist from file."""
        with open(self.allowlist_path, encoding="utf-8") as f:
            return json.load(f)

    def _classify_seam(self, seam: dict[str, Any]) -> tuple[str, str]:
        """Classify a single seam and return (reason_code, justification)."""
        file_path = seam["file_path"]
        function_name = seam["function_name"]
        imported_modules = seam.get("imported_modules", [])
        imported_symbols = seam.get("imported_symbols", [])

        # D1_EXTERNAL_OPTIONAL_DEP: External optional dependencies
        external_deps = {
            "pinecone",
            "redis",
            "torch",
            "transformers",
            "openai",
            "anthropic",
            "numpy",
            "pandas",
            "matplotlib",
            "plotly",
        }

        for module in imported_modules:
            if any(dep in module.lower() for dep in external_deps):
                return ("D1_EXTERNAL_OPTIONAL_DEP", f"Optional external dependency: {module}")

        for module, symbol in imported_symbols:
            if any(dep in module.lower() for dep in external_deps):
                return ("D1_EXTERNAL_OPTIONAL_DEP", f"Optional external dependency: {module}.{symbol}")

        # D2_ENTRYPOINT_SCRIPT: Scripts and orchestration
        if (
            "scripts" in file_path
            or "ops_scripts" in file_path
            or function_name.endswith("_orchestrator")
            or function_name.endswith("_runner")
        ):
            return ("D2_ENTRYPOINT_SCRIPT", "Script/orchestration entrypoint with lazy loading")

        # D3_PLUGIN_REGISTRY_DISPATCH: Dynamic dispatch and registry
        registry_keywords = {
            "registry",
            "dispatch",
            "factory",
            "router",
            "broker",
            "agent",
            "sovereign",
            "mcp",
            "workflow",
        }

        if any(keyword in function_name.lower() for keyword in registry_keywords) or any(
            keyword in file_path.lower() for keyword in registry_keywords
        ):
            return ("D3_PLUGIN_REGISTRY_DISPATCH", "Plugin registry or dynamic dispatch boundary")

        # D4_OBSERVABILITY_INTEGRATION: Telemetry and monitoring
        obs_keywords = {
            "telemetry",
            "tracing",
            "metrics",
            "observability",
            "monitoring",
            "logging",
            "reporting",
        }

        if (
            any(keyword in function_name.lower() for keyword in obs_keywords)
            or "L6_observability" in file_path
        ):
            return ("D4_OBSERVABILITY_INTEGRATION", "Observability/telemetry integration point")

        # D5_SECURITY_SAFETY_ADAPTER: Safety and policy adapters
        safety_keywords = {
            "safety",
            "security",
            "validator",
            "enforcement",
            "guard",
            "policy",
            "archival",
            "healing",
            "adapter",
        }

        if (
            any(keyword in function_name.lower() for keyword in safety_keywords)
            or "L5_safety" in file_path
            or "enforcement" in file_path
        ):
            return ("D5_SECURITY_SAFETY_ADAPTER", "Security/safety adapter or policy boundary")

        # Default classification for remaining seams
        return ("D3_PLUGIN_REGISTRY_DISPATCH", "Dynamic component loading (default classification)")

    def classify_all_seams(self) -> None:
        """Classify all seams in the allowlist."""
        classified_count = 0

        for seam in self.allowlist_data["seams"]:
            if seam["reason_code"] == "TBD":
                reason_code, justification = self._classify_seam(seam)
                seam["reason_code"] = reason_code
                seam["justification"] = justification
                classified_count += 1

        print(f"Classified {classified_count} seams")

        # Update total count
        self.allowlist_data["total_seams"] = len(self.allowlist_data["seams"])

    def save_allowlist(self) -> None:
        """Save updated allowlist to file."""
        _wg.write_json(self.allowlist_path, self.allowlist_data, indent=2)

    def print_summary(self) -> None:
        """Print classification summary."""
        reason_counts = {}
        for seam in self.allowlist_data["seams"]:
            reason = seam["reason_code"]
            reason_counts[reason] = reason_counts.get(reason, 0) + 1

        print("\nClassification Summary:")
        for reason, count in sorted(reason_counts.items()):
            description = self.REASON_TAXONOMY.get(reason, "Unknown")
            print(f"  {reason}: {count} - {description}")


def main():
    """Main execution."""
    root_path = Path.cwd()
    allowlist_path = root_path / AGENTIC_CORE_DIR / "L5_safety" / "governance" / "lazy_seam_allowlist.json"

    classifier = LazySeamClassifier(allowlist_path)
    classifier.classify_all_seams()
    classifier.save_allowlist()
    classifier.print_summary()

    print(f"\nUpdated allowlist saved to: {allowlist_path}")


if __name__ == "__main__":
    main()
