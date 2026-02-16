"""
Phase 7: Orphan Agent Detection (The Genealogist)
==================================================
Zero-Trust Guardian Layer for detecting unused/orphan agents.

This test suite identifies agents that exist in the codebase but are:
1. Never imported by other modules
2. Never instantiated or referenced
3. Have no test coverage
4. Candidates for deprecation, merge, or deletion

MANDATORY TEST CASES:
1. test_orphan_agent_detection: Identify agents with no external references
2. test_orphan_disposition_recommendations: Generate actionable recommendations
3. test_orphan_agent_report_generation: Create detailed report with diffs

USAGE:
    pytest tests/guardian/test_orphan_agent_detection.py -v -m guardian

EXPECTED RESULT:
    Report generation with disposition recommendations for each orphan agent
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import pytest

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================================
# GUARDIAN MARKER - All tests in this file are tagged for guardian runs
# =============================================================================
pytestmark = pytest.mark.guardian


# =============================================================================
# DISPOSITION CATEGORIES
# =============================================================================


class Disposition(Enum):
    """Recommended disposition for orphan agents."""

    DELETE = "DELETE"  # No value, safe to remove
    DEPRECATE = "DEPRECATE"  # Mark deprecated, schedule removal
    MERGE = "MERGE"  # Consolidate with another agent
    FIX = "FIX"  # Has value but needs integration
    ARCHIVE = "ARCHIVE"  # Move to legacy_archive
    KEEP = "KEEP"  # False positive, actually used


@dataclass
class OrphanAgent:
    """Data class for orphan agent information."""

    class_name: str
    file_path: str
    layer: str
    territory: str
    loc: int
    references: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    test_files: list[str] = field(default_factory=list)
    disposition: Disposition = Disposition.DELETE
    disposition_reason: str = ""
    merge_target: str | None = None
    has_healing: bool = False
    has_subatomic: bool = False
    cyclomatic_complexity: int = 0


# =============================================================================
# ORPHAN DETECTION ENGINE
# =============================================================================


class OrphanAgentDetector:
    """Detects orphan agents and generates disposition recommendations."""

    # Directories to skip during scanning
    SKIP_DIRS = frozenset(
        {
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            "env",
            ".pytest_cache",
            ".mypy_cache",
            ".tox",
            "node_modules",
            ".vscode",
            ".idea",
            "dist",
            "build",
            ".backup",
            "legacy_archive",
        },
    )

    # Known agent patterns that should be kept
    PROTECTED_AGENTS = frozenset(
        {
            "SovereignBaseAgent",
            "L0RoutingBaseAgent",
            "L1CognitionBase",
            "L2ExecutionBase",
            "L3OrchestrationBase",
            "L4StateBase",
            "L5SafetyBase",
            "L6ObservabilityBase",
            "RGAgentBase",
            "LICAgentBase",
        },
    )

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.agents: list[dict[str, Any]] = []
        self.agent_classes: set[str] = set()
        self.agent_files: dict[str, str] = {}
        self.all_references: dict[str, set[str]] = defaultdict(set)
        self.all_imports: dict[str, set[str]] = defaultdict(set)
        self.orphans: list[OrphanAgent] = []

    def load_agent_discovery(self) -> list[dict[str, Any]]:
        """Load agent discovery data from SSOT JSON."""
        discovery_path = self.project_root / "agent_discovery_full.json"
        if not discovery_path.exists():
            raise FileNotFoundError(f"agent_discovery_full.json not found at {discovery_path}")

        with open(discovery_path, encoding="utf-8") as f:
            data = json.load(f)

        # Support both v54 schema (dict with "agents" key) and legacy (flat list)
        if isinstance(data, dict) and "agents" in data:
            self.agents = data["agents"]
        elif isinstance(data, list):
            self.agents = data
        else:
            self.agents = []

        self.agent_classes = {agent["class_name"] for agent in self.agents}
        self.agent_files = {
            agent["class_name"]: agent.get("file", agent.get("path", "")) for agent in self.agents
        }

        return self.agents

    def scan_references(self) -> None:
        """Scan codebase for agent imports and references using optimized approach."""
        # Build a single combined regex pattern for all agents (much faster)
        agent_list = list(self.agent_classes)
        if not agent_list:
            return

        # Create combined pattern: \b(Agent1|Agent2|Agent3)\b
        combined_pattern = re.compile(r"\b(" + "|".join(re.escape(a) for a in agent_list) + r")\b")

        files_scanned = 0

        for root, dirs, files in os.walk(self.project_root):
            # Skip problematic directories early
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]

            for file in files:
                if not file.endswith(".py"):
                    continue

                file_path = Path(root) / file
                rel_path = str(file_path.relative_to(self.project_root)).replace("\\", "/")

                try:
                    content = file_path.read_text(encoding="utf-8")
                    files_scanned += 1

                    # Find all agent references in one pass
                    matches = combined_pattern.findall(content)
                    for match in matches:
                        if match in self.agent_classes:
                            self.all_references[match].add(rel_path)

                    # Find imports of agents
                    import_matches = re.findall(
                        r"(?:from\s+\S+\s+)?import\s+([A-Z][a-zA-Z0-9]*Agent)",
                        content,
                    )
                    for match in import_matches:
                        if match in self.agent_classes:
                            self.all_imports[match].add(rel_path)

                except Exception:
                    continue

        print(f"  Scanned {files_scanned} Python files")

    def identify_orphans(self) -> list[OrphanAgent]:
        """Identify orphan agents based on reference analysis."""
        self.orphans = []

        # Patterns for non-production files
        NON_PROD_PATTERNS = {
            "/tests/",
            "test_",
            "_test.py",
            "conftest.py",
            "discovery",
            "audit",
            "report",
            "ops_scripts/",
            "scripts/",
        }

        for agent in self.agents:
            class_name = agent["class_name"]

            # Skip protected base agents
            if class_name in self.PROTECTED_AGENTS:
                continue

            # Get agent's own file path (normalized)
            own_file = agent.get("file", agent.get("path", "")).replace("\\", "/")

            # Get all references excluding own file
            refs = self.all_references.get(class_name, set())
            non_self_refs = {r for r in refs if r != own_file}

            # Separate production and non-production references
            prod_refs = set()
            test_refs = set()
            for ref in non_self_refs:
                is_non_prod = any(pattern in ref for pattern in NON_PROD_PATTERNS)
                if is_non_prod:
                    test_refs.add(ref)
                else:
                    prod_refs.add(ref)

            # Determine if orphan based on production usage
            # An agent is orphan if it has NO production references
            is_orphan = len(prod_refs) == 0

            if is_orphan:
                orphan = OrphanAgent(
                    class_name=class_name,
                    file_path=own_file,
                    layer=agent.get("layer", "Unknown"),
                    territory=agent.get("territory", agent.get("layer", "Unknown")),
                    loc=agent.get("loc", 0),
                    references=list(non_self_refs),
                    imports=list(self.all_imports.get(class_name, set())),
                    test_files=list(test_refs),
                    has_healing=agent.get("has_healing", False),
                    has_subatomic=agent.get("has_subatomic", False),
                    cyclomatic_complexity=agent.get("cyclomatic_complexity", 0),
                )
                self.orphans.append(orphan)

        return self.orphans

    def generate_dispositions(self) -> None:
        """Generate disposition recommendations for each orphan."""
        for orphan in self.orphans:
            disposition, reason, merge_target = self._analyze_disposition(orphan)
            orphan.disposition = disposition
            orphan.disposition_reason = reason
            orphan.merge_target = merge_target

    def _analyze_disposition(self, orphan: OrphanAgent) -> tuple[Disposition, str, str | None]:
        """Analyze an orphan agent and recommend disposition."""
        # Check if in legacy_archive - already deprecated
        if "legacy_archive" in orphan.file_path:
            return (
                Disposition.DELETE,
                "Already in legacy_archive, safe to delete",
                None,
            )

        # Check if it has test coverage
        has_tests = len(orphan.test_files) > 0

        # Check if it's a small utility agent
        is_small = orphan.loc < 50

        # Check if it has healing capabilities
        has_healing = orphan.has_healing

        # Check complexity
        is_complex = orphan.cyclomatic_complexity > 20

        # Decision tree for disposition
        if is_small and not has_tests and not has_healing:
            return (
                Disposition.DELETE,
                f"Small agent ({orphan.loc} LOC), no tests, no healing - safe to delete",
                None,
            )

        if is_small and not is_complex:
            # Look for potential merge targets
            merge_target = self._find_merge_target(orphan)
            if merge_target:
                return (
                    Disposition.MERGE,
                    f"Small agent, consider merging into {merge_target}",
                    merge_target,
                )

        if has_tests and not has_healing:
            return (
                Disposition.FIX,
                "Has test coverage but no production usage - needs integration",
                None,
            )

        if has_healing and is_complex:
            return (
                Disposition.ARCHIVE,
                "Complex agent with healing - archive for potential future use",
                None,
            )

        if "HOP" in orphan.class_name:
            return (
                Disposition.KEEP,
                "HOP pipeline agent - may be used dynamically",
                None,
            )

        # Default: deprecate
        return (
            Disposition.DEPRECATE,
            "No clear usage pattern - mark for deprecation review",
            None,
        )

    def _find_merge_target(self, orphan: OrphanAgent) -> str | None:
        """Find a potential merge target for a small orphan agent."""
        # Look for agents in the same territory
        same_territory = [
            a["class_name"]
            for a in self.agents
            if a.get("territory", a.get("layer", "Unknown")) == orphan.territory
            and a["class_name"] != orphan.class_name
            and a["class_name"] not in [o.class_name for o in self.orphans]
        ]

        if same_territory:
            return same_territory[0]

        return None

    def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive orphan agent report."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_agents": len(self.agents),
            "orphan_count": len(self.orphans),
            "orphan_percentage": (len(self.orphans) / len(self.agents) * 100 if self.agents else 0),
            "disposition_summary": {},
            "orphans_by_layer": {},
            "orphans": [],
        }

        # Count by disposition
        for disp in Disposition:
            count = sum(1 for o in self.orphans if o.disposition == disp)
            if count > 0:
                report["disposition_summary"][disp.value] = count

        # Group by layer
        for orphan in self.orphans:
            layer = orphan.layer
            if layer not in report["orphans_by_layer"]:
                report["orphans_by_layer"][layer] = []
            report["orphans_by_layer"][layer].append(orphan.class_name)

        # Detailed orphan entries
        for orphan in sorted(self.orphans, key=lambda x: x.disposition.value):
            report["orphans"].append(
                {
                    "class_name": orphan.class_name,
                    "file_path": orphan.file_path,
                    "layer": orphan.layer,
                    "territory": orphan.territory,
                    "loc": orphan.loc,
                    "disposition": orphan.disposition.value,
                    "disposition_reason": orphan.disposition_reason,
                    "merge_target": orphan.merge_target,
                    "reference_count": len(orphan.references),
                    "test_count": len(orphan.test_files),
                    "has_healing": orphan.has_healing,
                    "cyclomatic_complexity": orphan.cyclomatic_complexity,
                },
            )

        return report


# =============================================================================
# TEST CLASS
# =============================================================================


class TestOrphanAgentDetection:
    """Guardian tests for orphan agent detection."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.project_root = PROJECT_ROOT
        self.detector = OrphanAgentDetector(self.project_root)

    def test_orphan_agent_detection(self):
        """
        MANDATORY TEST 1: Identify agents with no external references.

        Scans the codebase for agents that are defined but never imported
        or referenced by other production code.
        """
        print("\n=== PHASE 7 MANDATORY: Orphan Agent Detection ===")

        # Load agent discovery data
        agents = self.detector.load_agent_discovery()
        print(f"  Total agents in discovery: {len(agents)}")

        # Scan for references
        print("\n  Scanning codebase for agent references...")
        self.detector.scan_references()

        # Identify orphans
        orphans = self.detector.identify_orphans()
        print(f"\n  Orphan agents identified: {len(orphans)}")

        # Report findings
        if orphans:
            print("\n  Orphan agents (no production references):")
            for orphan in orphans[:20]:  # Show first 20
                print(f"    - {orphan.class_name} ({orphan.file_path})")
            if len(orphans) > 20:
                print(f"    ... and {len(orphans) - 20} more")

        # Track as tech debt - allow up to 30% orphan rate
        orphan_rate = len(orphans) / len(agents) * 100 if agents else 0
        ORPHAN_THRESHOLD = 30.0

        if orphan_rate > ORPHAN_THRESHOLD:
            print(f"\n[WARNING] Orphan rate ({orphan_rate:.1f}%) exceeds threshold")
        else:
            print(f"\n[OK] Orphan rate ({orphan_rate:.1f}%) within acceptable range")

        print("\n[OK] Orphan agent detection complete")

    def test_orphan_disposition_recommendations(self):
        """
        MANDATORY TEST 2: Generate actionable disposition recommendations.

        Analyzes each orphan agent and recommends:
        - DELETE: Safe to remove
        - DEPRECATE: Mark for future removal
        - MERGE: Consolidate with another agent
        - FIX: Needs integration work
        - ARCHIVE: Move to legacy_archive
        - KEEP: False positive
        """
        print("\n=== PHASE 7 MANDATORY: Disposition Recommendations ===")

        # Load and scan
        self.detector.load_agent_discovery()
        self.detector.scan_references()
        self.detector.identify_orphans()

        # Generate dispositions
        self.detector.generate_dispositions()

        # Report by disposition
        print("\n  Disposition Summary:")
        disposition_counts: dict[Disposition, int] = {}
        for orphan in self.detector.orphans:
            disposition_counts[orphan.disposition] = disposition_counts.get(orphan.disposition, 0) + 1

        for disp, count in sorted(disposition_counts.items(), key=lambda x: -x[1]):
            print(f"    {disp.value}: {count} agents")

        # Show detailed recommendations
        print("\n  Detailed Recommendations:")
        for disp in [Disposition.DELETE, Disposition.MERGE, Disposition.DEPRECATE]:
            agents_with_disp = [o for o in self.detector.orphans if o.disposition == disp]
            if agents_with_disp:
                print(f"\n    [{disp.value}]:")
                for orphan in agents_with_disp[:5]:
                    print(f"      - {orphan.class_name}")
                    print(f"        Reason: {orphan.disposition_reason}")
                    if orphan.merge_target:
                        print(f"        Merge into: {orphan.merge_target}")
                if len(agents_with_disp) > 5:
                    print(f"      ... and {len(agents_with_disp) - 5} more")

        print("\n[OK] Disposition recommendations generated")

    def test_orphan_agent_report_generation(self):
        """
        MANDATORY TEST 3: Create detailed report with all orphan information.

        Generates a comprehensive JSON report saved to logs/compliance_reports/
        """
        print("\n=== PHASE 7 MANDATORY: Report Generation ===")

        # Full analysis
        self.detector.load_agent_discovery()
        self.detector.scan_references()
        self.detector.identify_orphans()
        self.detector.generate_dispositions()

        # Generate report
        report = self.detector.generate_report()

        # Save report
        report_dir = self.project_root / "logs" / "compliance_reports"
        report_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = report_dir / f"orphan_agent_report_{timestamp}.json"

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"  Report saved to: {report_path}")
        print("\n  Summary:")
        print(f"    Total agents: {report['total_agents']}")
        print(f"    Orphan agents: {report['orphan_count']}")
        print(f"    Orphan rate: {report['orphan_percentage']:.1f}%")
        print("\n  Disposition breakdown:")
        for disp, count in report["disposition_summary"].items():
            print(f"    {disp}: {count}")

        print("\n[OK] Report generation complete")

        # Store report for potential further analysis (don't return from test)
        self._last_report = report


# =============================================================================
# STANDALONE EXECUTION
# =============================================================================


def generate_orphan_report() -> dict[str, Any]:
    """Generate orphan agent report without pytest."""
    detector = OrphanAgentDetector(PROJECT_ROOT)
    detector.load_agent_discovery()
    detector.scan_references()
    detector.identify_orphans()
    detector.generate_dispositions()
    return detector.generate_report()


if __name__ == "__main__":
    print("=" * 80)
    print("ORPHAN AGENT DETECTION - Guardian Test Suite")
    print("=" * 80)

    # Create detector directly for standalone execution
    detector = OrphanAgentDetector(PROJECT_ROOT)

    print("\n=== PHASE 7 MANDATORY: Orphan Agent Detection ===")
    agents = detector.load_agent_discovery()
    print(f"  Total agents in discovery: {len(agents)}")

    print("\n  Scanning codebase for agent references...")
    detector.scan_references()

    orphans = detector.identify_orphans()
    print(f"\n  Orphan agents identified: {len(orphans)}")

    if orphans:
        print("\n  Orphan agents (no production references):")
        for orphan in orphans[:20]:
            print(f"    - {orphan.class_name} ({orphan.file_path})")
        if len(orphans) > 20:
            print(f"    ... and {len(orphans) - 20} more")

    print("\n=== PHASE 7 MANDATORY: Disposition Recommendations ===")
    detector.generate_dispositions()

    disposition_counts: dict[Disposition, int] = {}
    for orphan in detector.orphans:
        disposition_counts[orphan.disposition] = disposition_counts.get(orphan.disposition, 0) + 1

    print("\n  Disposition Summary:")
    for disp, count in sorted(disposition_counts.items(), key=lambda x: -x[1]):
        print(f"    {disp.value}: {count} agents")

    print("\n  Detailed Recommendations:")
    for disp in [Disposition.DELETE, Disposition.MERGE, Disposition.DEPRECATE]:
        agents_with_disp = [o for o in detector.orphans if o.disposition == disp]
        if agents_with_disp:
            print(f"\n    [{disp.value}]:")
            for orphan in agents_with_disp[:5]:
                print(f"      - {orphan.class_name}")
                print(f"        Reason: {orphan.disposition_reason}")
                if orphan.merge_target:
                    print(f"        Merge into: {orphan.merge_target}")
            if len(agents_with_disp) > 5:
                print(f"      ... and {len(agents_with_disp) - 5} more")

    print("\n=== PHASE 7 MANDATORY: Report Generation ===")
    report = detector.generate_report()

    report_dir = PROJECT_ROOT / "logs" / "compliance_reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"orphan_agent_report_{timestamp}.json"

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"  Report saved to: {report_path}")
    print("\n  Summary:")
    print(f"    Total agents: {report['total_agents']}")
    print(f"    Orphan agents: {report['orphan_count']}")
    print(f"    Orphan rate: {report['orphan_percentage']:.1f}%")

    print("\n" + "=" * 80)
    print("ORPHAN AGENT REPORT COMPLETE")
    print("=" * 80)
