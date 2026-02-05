#!/usr/bin/env python
"""
Misc Liquidation Scanner: Forensic Content Triage
Analyzes docs/reports/misc/ files for semantic reclassification
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path


class MiscLiquidationScanner:
    """Forensic scanner for misc/ folder liquidation."""

    # Existing L4 categories
    EXISTING_CATEGORIES = {
        "audit": {
            "keywords": [
                "audit",
                "drift",
                "variance",
                "compliance",
                "ssot",
                "violation",
                "integrity",
            ],
            "headers": ["# Audit", "## Violations", "## Drift", "## Compliance"],
            "json_keys": ["violations", "drift_metrics", "compliance_score"],
        },
        "assessments": {
            "keywords": [
                "assessment",
                "analysis",
                "gap",
                "architecture",
                "strategic",
                "recommendation",
            ],
            "headers": ["# Assessment", "## Analysis", "## Recommendations", "## Gap"],
            "json_keys": ["assessment_summary", "recommendations", "gap_analysis"],
        },
        "coverage": {
            "keywords": ["coverage", "test", "quality", "percentage", "htmlcov"],
            "headers": ["# Coverage", "## Test Results", "## Quality"],
            "json_keys": ["coverage_percentage", "test_results", "quality_metrics"],
        },
        "telemetry": {
            "keywords": ["telemetry", "metrics", "performance", "observability", "dashboard"],
            "headers": ["# Telemetry", "## Metrics", "## Performance"],
            "json_keys": ["telemetry", "metrics", "performance_data"],
        },
        "security": {
            "keywords": ["security", "vulnerability", "safety", "hardened", "guardrails"],
            "headers": ["# Security", "## Vulnerabilities", "## Safety"],
            "json_keys": ["security_scan", "vulnerabilities", "safety_check"],
        },
        "missions": {
            "keywords": ["mission", "trace", "execution", "runtime"],
            "headers": ["# Mission", "## Execution", "## Trace"],
            "json_keys": ["mission_id", "trace_id", "execution_log"],
        },
    }

    # Potential new categories
    NEW_CATEGORIES = {
        "legacy": {
            "keywords": ["deprecated", "obsolete", "archived", "old", "legacy", "phase"],
            "date_patterns": [r"202[0-4]", r"phase\d+", r"v\d+\.\d+"],
            "file_patterns": [r".*_old\..*", r".*_deprecated\..*", r".*_archived\..*"],
        },
        "governance": {
            "keywords": ["governance", "policy", "mapping", "versioning", "manifest", "registry"],
            "headers": ["# Governance", "## Policy", "## Mapping"],
            "json_keys": ["governance", "policy", "version_registry"],
        },
        "prototypes": {
            "keywords": ["prototype", "experimental", "poc", "demo", "sample", "example"],
            "headers": ["# Prototype", "## Experimental", "## Demo"],
            "json_keys": ["prototype", "experimental", "demo"],
        },
    }

    def __init__(self, misc_dir: Path):
        self.misc_dir = misc_dir
        self.classifications: dict[str, list[dict]] = defaultdict(list)
        self.stats = {"total_files": 0, "classified": 0, "unclassified": 0}

    def scan_all_files(self) -> None:
        """Scan all files in misc/ directory."""
        if not self.misc_dir.exists():
            print(f"Directory not found: {self.misc_dir}")
            return

        files = list(self.misc_dir.rglob("*"))
        files = [f for f in files if f.is_file()]

        self.stats["total_files"] = len(files)

        print(f"Scanning {len(files)} files...")

        for file_path in files:
            classification = self._classify_file(file_path)

            if classification:
                self.classifications[classification["category"]].append(
                    {
                        "file": file_path.name,
                        "path": str(file_path.relative_to(self.misc_dir.parent.parent.parent)),
                        "signals": classification["signals"],
                        "confidence": classification["confidence"],
                    }
                )
                self.stats["classified"] += 1
            else:
                self.classifications["unclassified"].append(
                    {
                        "file": file_path.name,
                        "path": str(file_path.relative_to(self.misc_dir.parent.parent.parent)),
                        "signals": [],
                        "confidence": 0,
                    }
                )
                self.stats["unclassified"] += 1

    def _classify_file(self, file_path: Path) -> dict | None:
        """Classify a single file based on content."""
        # Read first 1000 characters
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read(1000).lower()
        except (UnicodeDecodeError, PermissionError):
            return None

        # Score each category
        scores = {}
        signals_found = {}

        # Check existing categories
        for category, patterns in self.EXISTING_CATEGORIES.items():
            score = 0
            signals = []

            # Check keywords
            for keyword in patterns["keywords"]:
                if keyword in content:
                    score += 2
                    signals.append(f"keyword:{keyword}")

            # Check headers (markdown)
            for header in patterns.get("headers", []):
                if header.lower() in content:
                    score += 3
                    signals.append(f"header:{header}")

            # Check JSON keys
            for json_key in patterns.get("json_keys", []):
                if f'"{json_key}"' in content or f"'{json_key}'" in content:
                    score += 2
                    signals.append(f"json_key:{json_key}")

            if score > 0:
                scores[category] = score
                signals_found[category] = signals

        # Check new categories
        for category, patterns in self.NEW_CATEGORIES.items():
            score = 0
            signals = []

            # Check keywords
            for keyword in patterns["keywords"]:
                if keyword in content:
                    score += 2
                    signals.append(f"keyword:{keyword}")

            # Check date patterns
            for date_pattern in patterns.get("date_patterns", []):
                if re.search(date_pattern, content):
                    score += 1
                    signals.append(f"date_pattern:{date_pattern}")

            # Check file patterns
            for file_pattern in patterns.get("file_patterns", []):
                if re.match(file_pattern, file_path.name.lower()):
                    score += 3
                    signals.append(f"file_pattern:{file_pattern}")

            if score > 0:
                scores[category] = score
                signals_found[category] = signals

        # Return highest scoring category
        if scores:
            best_category = max(scores.items(), key=lambda x: x[1])
            return {
                "category": best_category[0],
                "confidence": best_category[1],
                "signals": signals_found[best_category[0]],
            }

        return None

    def generate_mapping_table(self) -> str:
        """Generate mapping table for review."""
        lines = [
            "# Misc Liquidation: Zero-Misc Distribution Plan",
            "",
            f"**Scan Date:** {datetime.now().isoformat()}",
            "**Target Directory:** `docs/reports/misc/`",
            f"**Total Files:** {self.stats['total_files']}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            f"**Classified:** {self.stats['classified']} files ({self.stats['classified'] / self.stats['total_files'] * 100:.1f}%)",
            f"**Unclassified:** {self.stats['unclassified']} files ({self.stats['unclassified'] / self.stats['total_files'] * 100:.1f}%)",
            "",
            "---",
            "",
            "## Distribution Plan",
            "",
        ]

        # Sort categories by file count
        sorted_categories = sorted(
            [(cat, files) for cat, files in self.classifications.items()],
            key=lambda x: len(x[1]),
            reverse=True,
        )

        for category, files in sorted_categories:
            if category == "unclassified":
                continue

            is_new = category in self.NEW_CATEGORIES
            status = "🆕 NEW CATEGORY" if is_new else "✅ EXISTING"

            lines.append(f"### {category}/ ({status})")
            lines.append("")
            lines.append(f"**File Count:** {len(files)}")
            lines.append("")

            # Show top signals
            all_signals = []
            for file_info in files:
                all_signals.extend(file_info["signals"])

            signal_counts = defaultdict(int)
            for signal in all_signals:
                signal_counts[signal] += 1

            top_signals = sorted(signal_counts.items(), key=lambda x: x[1], reverse=True)[:5]

            if top_signals:
                lines.append("**Top Signals:**")
                for signal, count in top_signals:
                    lines.append(f"- `{signal}` ({count} files)")
                lines.append("")

            # Show sample files
            lines.append("**Sample Files:**")
            for file_info in files[:5]:
                lines.append(f"- `{file_info['file']}` (confidence: {file_info['confidence']})")

            if len(files) > 5:
                lines.append(f"- ... and {len(files) - 5} more")

            lines.append("")

        # Unclassified files
        if "unclassified" in self.classifications:
            unclassified = self.classifications["unclassified"]
            lines.append("### ⚠️ Unclassified Files")
            lines.append("")
            lines.append(f"**File Count:** {len(unclassified)}")
            lines.append("")
            lines.append(
                "**Recommendation:** Manual review or create `docs/reports/misc_archive/` for truly uncategorizable files"
            )
            lines.append("")
            lines.append("**Sample Files:**")
            for file_info in unclassified[:10]:
                lines.append(f"- `{file_info['file']}`")
            if len(unclassified) > 10:
                lines.append(f"- ... and {len(unclassified) - 10} more")
            lines.append("")

        lines.extend(
            [
                "---",
                "",
                "## Proposed Actions",
                "",
                "### Existing Categories (Move to existing L4 folders)",
                "",
            ]
        )

        for category in ["audit", "assessments", "coverage", "telemetry", "security", "missions"]:
            if category in self.classifications:
                count = len(self.classifications[category])
                lines.append(f"- **{category}/**: {count} files → `docs/reports/{category}/`")

        lines.append("")
        lines.append("### New Categories (Create new L4 folders)")
        lines.append("")

        for category in ["legacy", "governance", "prototypes"]:
            if category in self.classifications:
                count = len(self.classifications[category])
                lines.append(f"- **{category}/**: {count} files → `docs/reports/{category}/` (NEW)")

        lines.extend(
            [
                "",
                "---",
                "",
                "## Constitutional Amendment Required",
                "",
                "If new categories are approved, update `structure_blueprint_config.py`:",
                "",
                "```python",
                '"docs": {',
                '    "subfolders": {',
                '        "reports": {',
                '            "subfolders": {',
                '                "assessments": {...},',
                '                "audit": {...},',
                '                "coverage": {...},',
                '                "security": {...},',
                '                "telemetry": {...},',
                '                "missions": {...},',
            ]
        )

        for category in ["legacy", "governance", "prototypes"]:
            if category in self.classifications and len(self.classifications[category]) > 0:
                purpose = (
                    self.NEW_CATEGORIES[category]["keywords"][0].title()
                    + " artifacts and documentation"
                )
                lines.append(f'                "{category}": {{"purpose": "{purpose}"}},')

        lines.extend(
            [
                "            }",
                "        }",
                "    }",
                "}",
                "```",
                "",
                "---",
                "",
                "## ⚠️ DECISION GATE: AWAITING APPROVAL",
                "",
                "Review the distribution plan above before proceeding to execution.",
                "",
            ]
        )

        return "\n".join(lines)


def main():
    """Execute misc liquidation scan."""
    root = Path("C:/Git/Agentic-Workflow")
    misc_dir = root / "docs" / "reports" / "misc"

    print("=" * 70)
    print("MISC LIQUIDATION: FORENSIC CONTENT TRIAGE")
    print("=" * 70)
    print()

    scanner = MiscLiquidationScanner(misc_dir)

    print("[1/2] Scanning files for semantic classification...")
    scanner.scan_all_files()
    print(f"      Total files: {scanner.stats['total_files']}")
    print(f"      Classified: {scanner.stats['classified']}")
    print(f"      Unclassified: {scanner.stats['unclassified']}")
    print()

    print("[2/2] Generating distribution plan...")
    mapping_table = scanner.generate_mapping_table()

    report_path = root / "misc_liquidation_plan.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(mapping_table)

    # Save detailed JSON
    json_path = root / "misc_liquidation_plan.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "stats": scanner.stats,
                "classifications": dict(scanner.classifications.items()),
            },
            f,
            indent=2,
        )

    print(f"      Report saved: {report_path}")
    print(f"      JSON saved: {json_path}")
    print()

    print("=" * 70)
    print("DISTRIBUTION PLAN READY FOR REVIEW")
    print("=" * 70)
    print()

    # Print summary
    for category, files in sorted(
        scanner.classifications.items(), key=lambda x: len(x[1]), reverse=True
    ):
        is_new = category in scanner.NEW_CATEGORIES
        marker = "🆕" if is_new else "✅"
        print(f"  {marker} {category}/: {len(files)} files")

    print()
    print("⚠️  AWAITING APPROVAL - DO NOT PROCEED TO EXECUTION")


if __name__ == "__main__":
    main()
