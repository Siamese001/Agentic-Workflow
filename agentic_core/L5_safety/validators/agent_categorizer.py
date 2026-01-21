"""
AST-based agent categorization for dashboard display.
Creates non-overlapping categories based on agent class patterns and docstrings.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from agentic_core.utils.sovereign_index import SovereignIndex


class AgentCategorizer:
    """Categorizes agents into non-overlapping groups based on AST analysis."""

    # Non-overlapping category patterns (ordered by priority)
    CATEGORY_PATTERNS = [
        {
            "name": "Validation & Compliance",
            "patterns": [
                r"Validator|Validation",
                r"Compliance|Enforce",
                r"Check|Verify|Audit",
                r"SSOT|Constitution",
            ],
            "exclude": [r"Heal|Repair|Fix", r"Guard|Protect|Safety"],
        },
        {
            "name": "Self-Healing & Recovery",
            "patterns": [
                r"Healer|Healing",
                r"Repair|Fix|Recovery",
                r"Reconcile|Restore",
            ],
            "exclude": [r"Validator|Compliance"],
        },
        {
            "name": "Safety & Security",
            "patterns": [
                r"Guardian|Guard",
                r"Safety|Security",
                r"Protect|Defense",
                r"Sentinel|Watchdog",
                r"Immune|Threat",
            ],
            "exclude": [r"Validator|Healer"],
        },
        {
            "name": "Code Quality & Analysis",
            "patterns": [
                r"Analyzer|Analysis",
                r"Detector|Detection",
                r"Hunter|Finder",
                r"Formatter|Format",
                r"Deduplicat|Duplicate",
                r"Cleanup|Clean",
                r"Unused|Prune",
            ],
            "exclude": [r"Validator|Healer|Guardian"],
        },
        {
            "name": "Governance & Architecture",
            "patterns": [
                r"Governor|Governance",
                r"Architect|Architecture",
                r"Hierarchy|Hierarchical",
                r"Location|Territory",
                r"Import|Gravity",
            ],
            "exclude": [r"Validator|Healer|Guardian"],
        },
        {
            "name": "Orchestration & Routing",
            "patterns": [
                r"Orchestrator|Orchestration",
                r"Router|Route|Routing",
                r"Conductor|Coordinate",
                r"Scheduler|Schedule",
            ],
            "exclude": [r"Validator|Healer"],
        },
        {
            "name": "Observability & Monitoring",
            "patterns": [
                r"Monitor|Monitoring",
                r"Metric|Metrics",
                r"Telemetry|Trace|Tracing",
                r"Logger|Logging",
                r"Report|Reporting",
            ],
            "exclude": [r"Validator|Healer"],
        },
        {
            "name": "Testing & Verification",
            "patterns": [
                r"Test|Testing",
                r"Oracle|Prophecy",
                r"Regression|Coverage",
                r"Verify|Verification",
            ],
            "exclude": [r"Validator|Healer"],
        },
        {
            "name": "Specialized Agents",
            "patterns": [
                r".*Agent",  # Catch-all for remaining agents
            ],
            "exclude": [],
        },
    ]

    def __init__(self, folder_path: Path):
        self.folder_path = folder_path
        self.agents: Dict[str, Dict] = {}
        self.categories: Dict[str, List[str]] = defaultdict(list)

    def scan_folder(self) -> Dict[str, List[str]]:
        """Scan folder and categorize all agents."""
        # Sub-20: Use ssot_discovery instead of glob
        from agentic_core.utils.ssot_discovery import get_python_files
        py_files = list(get_python_files(self.folder_path))

        for py_file in py_files:
            if py_file.name.startswith("__"):
                continue

            try:
                self._analyze_file(py_file)
            except (SyntaxError, UnicodeDecodeError):
                continue

        return dict(self.categories)

    def _analyze_file(self, py_file: Path) -> None:
        """Analyze a Python file and extract agent classes."""
        source = py_file.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                category = self._categorize_agent(node, source)
                self.categories[category].append(node.name)
                self.agents[node.name] = {
                    "file": py_file.name,
                    "category": category,
                    "docstring": ast.get_docstring(node) or "",
                }

    def _categorize_agent(self, class_node: ast.ClassDef, source: str) -> str:
        """Determine category for an agent based on name and docstring."""
        name = class_node.name
        docstring = ast.get_docstring(class_node) or ""
        combined_text = f"{name} {docstring}".lower()

        for category_def in self.CATEGORY_PATTERNS:
            # Check if any exclude pattern matches
            excluded = False
            for exclude_pattern in category_def["exclude"]:
                if re.search(exclude_pattern, combined_text, re.IGNORECASE):
                    excluded = True
                    break

            if excluded:
                continue

            # Check if any include pattern matches
            for pattern in category_def["patterns"]:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    return category_def["name"]

        return "Specialized Agents"

    def get_category_summary(self) -> Dict[str, int]:
        """Get count of agents per category."""
        return {cat: len(agents) for cat, agents in self.categories.items()}

    def get_agents_by_category(self, category: str) -> List[str]:
        """Get list of agents in a specific category."""
        return self.categories.get(category, [])


def categorize_agents_for_dashboard(folder_path: Path) -> Dict[str, List[str]]:
    """Main entry point for dashboard categorization."""
    categorizer = AgentCategorizer(folder_path)
    return categorizer.scan_folder()
