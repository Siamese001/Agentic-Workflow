#!/usr/bin/env python3
"""
ROOT CUSTOMS AGENT - Content-Aware Routing System
Enforces "Clean Root" policy by scanning and routing artifacts based on content signatures.
Uses ARTIFACT_ROUTING_MAP from structure_blueprint.py for semantic routing decisions.
"""

import json
import shutil
from pathlib import Path
from typing import Any
from dataclasses import dataclass

# Import the SSOT routing configuration
import sys

sys.path.append(str(Path(__file__).parent / "agentic_core" / "L5_safety" / "validators"))
from structure_blueprint import (
    ARTIFACT_ROUTING_MAP,
    ROOT_ALLOWED_PATTERNS,
    ROOT_PROTECTED_FILES,
    get_validated_project_root,
)


@dataclass
class RoutingDecision:
    """Represents a routing decision for a file."""

    file_path: Path
    destination: str | None
    reason: str
    confidence: float
    content_matches: dict[str, Any]
    is_protected: bool = False
    is_allowed_pattern: bool = False


class RootCustomsAgent:
    """
    The "Customs Agent" that inspects and routes files in the project root.
    Implements content-aware routing based on semantic signatures.
    """

    def __init__(self, project_root: Path | None = None, dry_run: bool = True):
        self.project_root = project_root or get_validated_project_root()
        self.dry_run = dry_run
        self.routing_decisions: list[RoutingDecision] = []

        print("🛃 Root Customs Agent Initialized")
        print(f"📁 Project Root: {self.project_root}")
        print(f"🔍 Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
        print()

    def scan_root_directory(self) -> list[Path]:
        """Scan the project root for files to analyze."""
        root_files = []

        for item in self.project_root.iterdir():
            if item.is_file():
                # Skip hidden files and protected files
                if not item.name.startswith(".") and item.name not in ROOT_PROTECTED_FILES:
                    root_files.append(item)

        print(f"📋 Found {len(root_files)} files in root to analyze")
        return root_files

    def check_allowed_patterns(self, file_path: Path) -> bool:
        """Check if file matches any allowed root patterns."""
        for pattern in ROOT_ALLOWED_PATTERNS:
            if pattern.match(file_path.name):
                return True
        return False

    def analyze_content_signatures(self, file_path: Path) -> dict[str, Any]:
        """Analyze file content for routing signatures."""
        content_matches = {}

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Check file extension
            ext = file_path.suffix.lower()

            # Analyze based on file type
            if ext == ".md":
                content_matches.update(self._analyze_markdown(content))
            elif ext == ".json":
                content_matches.update(self._analyze_json(content))
            else:
                content_matches.update(self._analyze_text(content))

        except Exception as e:
            content_matches["error"] = str(e)

        return content_matches

    def _analyze_markdown(self, content: str) -> dict[str, Any]:
        """Analyze markdown content for headers and keywords."""
        matches = {"headers": [], "keywords": []}

        # Extract headers
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                matches["headers"].append(line)

        # Check keywords
        content_lower = content.lower()
        for keyword in ["critical", "assessment", "findings", "report", "analysis"]:
            if keyword in content_lower:
                matches["keywords"].append(keyword)

        return matches

    def _analyze_json(self, content: str) -> dict[str, Any]:
        """Analyze JSON content for key signatures."""
        matches = {"json_keys": []}

        try:
            data = json.loads(content)

            def extract_keys(obj, prefix=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        full_key = f"{prefix}.{key}" if prefix else key
                        matches["json_keys"].append(key)
                        if isinstance(value, (dict, list)):
                            extract_keys(value, full_key)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        if isinstance(item, (dict, list)):
                            extract_keys(item, f"{prefix}[{i}]")

            extract_keys(data)

        except json.JSONDecodeError:
            matches["error"] = "Invalid JSON"

        return matches

    def _analyze_text(self, content: str) -> dict[str, Any]:
        """Analyze plain text content for keywords."""
        matches = {"keywords": []}

        # Common log/error keywords
        error_keywords = ["debug", "error", "exception", "traceback", "mission", "trace"]
        content_lower = content.lower()

        for keyword in error_keywords:
            if keyword in content_lower:
                matches["keywords"].append(keyword)

        return matches

    def determine_routing(
        self, file_path: Path, content_matches: dict[str, Any]
    ) -> RoutingDecision:
        """Determine where a file should be routed based on content analysis."""

        # Check if protected
        if file_path.name in ROOT_PROTECTED_FILES:
            return RoutingDecision(
                file_path=file_path,
                destination=None,
                reason="Protected file - cannot be moved",
                confidence=1.0,
                content_matches=content_matches,
                is_protected=True,
            )

        # Check if matches allowed patterns
        if self.check_allowed_patterns(file_path):
            return RoutingDecision(
                file_path=file_path,
                destination=None,
                reason="Matches allowed root pattern",
                confidence=1.0,
                content_matches=content_matches,
                is_allowed_pattern=True,
            )

        # Check against ARTIFACT_ROUTING_MAP
        best_match = None
        best_score = 0

        for destination, config in ARTIFACT_ROUTING_MAP.items():
            score = self._calculate_routing_score(file_path, content_matches, config)
            if score > best_score:
                best_score = score
                best_match = (destination, config)

        if best_match and best_score > 0:
            destination, config = best_match
            return RoutingDecision(
                file_path=file_path,
                destination=destination,
                reason=f"Content matches {destination} routing rules (score: {best_score:.2f})",
                confidence=best_score,
                content_matches=content_matches,
            )

        return RoutingDecision(
            file_path=file_path,
            destination=None,
            reason="No matching routing rule found",
            confidence=0.0,
            content_matches=content_matches,
        )

    def _calculate_routing_score(
        self, file_path: Path, content_matches: dict[str, Any], config: dict[str, Any]
    ) -> float:
        """Calculate routing score for a destination configuration."""
        score = 0.0

        # Check file extension
        ext = file_path.suffix.lower()
        if ext in config.get("file_extensions", []):
            score += 0.3

        # Check naming patterns
        for pattern in config.get("naming_patterns", []):
            if pattern.match(file_path.name):
                score += 0.3
                break

        # Check content signals
        content_signals = config.get("content_signals", {})

        # Headers
        if "headers" in content_matches:
            file_headers = [h.lower() for h in content_matches["headers"]]
            for header in content_signals.get("headers", []):
                if any(header.lower() in fh for fh in file_headers):
                    score += 0.2
                    break

        # JSON keys
        if "json_keys" in content_matches:
            file_keys = [k.lower() for k in content_matches["json_keys"]]
            for key in content_signals.get("json_keys", []):
                if any(key.lower() in fk for fk in file_keys):
                    score += 0.2
                    break

        # Keywords
        if "keywords" in content_matches:
            file_keywords = [k.lower() for k in content_matches["keywords"]]
            for keyword in content_signals.get("keywords", []):
                if any(keyword.lower() in fk for fk in file_keywords):
                    score += 0.1
                    break

        return min(score, 1.0)  # Cap at 1.0

    def execute_routing(self, decision: RoutingDecision) -> bool:
        """Execute a routing decision."""
        if not decision.destination or self.dry_run:
            return False

        source = decision.file_path
        target_dir = self.project_root / decision.destination
        target_file = target_dir / source.name

        try:
            # Create target directory if it doesn't exist
            target_dir.mkdir(parents=True, exist_ok=True)

            # Move the file
            shutil.move(str(source), str(target_file))
            print(f"✅ Moved: {source.name} → {decision.destination}/")
            return True

        except Exception as e:
            print(f"❌ Failed to move {source.name}: {e}")
            return False

    def run_inspection(self) -> dict[str, Any]:
        """Run complete root inspection and routing."""
        print("🔍 Starting Root Inspection...")
        print("=" * 60)

        root_files = self.scan_root_directory()

        for file_path in root_files:
            print(f"\n📄 Analyzing: {file_path.name}")

            # Analyze content
            content_matches = self.analyze_content_signatures(file_path)

            # Determine routing
            decision = self.determine_routing(file_path, content_matches)
            self.routing_decisions.append(decision)

            # Display decision
            status_icon = (
                "🛡️"
                if decision.is_protected
                else "✅"
                if decision.is_allowed_pattern
                else "📦"
                if decision.destination
                else "❓"
            )
            print(f"   {status_icon} {decision.reason}")

            if decision.destination:
                print(f"   🎯 Destination: {decision.destination}/")

            # Show content matches
            if decision.content_matches:
                for match_type, matches in decision.content_matches.items():
                    if matches and match_type != "error":
                        print(
                            f"   🔍 {match_type.title()}: {matches[:3]}{'...' if len(matches) > 3 else ''}"
                        )

        # Summary
        self._print_summary()

        # Execute routing if not dry run
        if not self.dry_run:
            print("\n🚀 Executing routing decisions...")
            moved_count = 0
            for decision in self.routing_decisions:
                if self.execute_routing(decision):
                    moved_count += 1
            print(f"✅ Moved {moved_count} files")

        return {
            "total_files": len(root_files),
            "routing_decisions": len(self.routing_decisions),
            "protected_files": sum(1 for d in self.routing_decisions if d.is_protected),
            "allowed_patterns": sum(1 for d in self.routing_decisions if d.is_allowed_pattern),
            "routed_files": sum(1 for d in self.routing_decisions if d.destination),
            "unmatched_files": sum(
                1
                for d in self.routing_decisions
                if not d.destination and not d.is_protected and not d.is_allowed_pattern
            ),
        }

    def _print_summary(self):
        """Print inspection summary."""
        print("\n" + "=" * 60)
        print("📊 ROOT INSPECTION SUMMARY")
        print("=" * 60)

        total = len(self.routing_decisions)
        protected = sum(1 for d in self.routing_decisions if d.is_protected)
        allowed = sum(1 for d in self.routing_decisions if d.is_allowed_pattern)
        routed = sum(1 for d in self.routing_decisions if d.destination)
        unmatched = sum(
            1
            for d in self.routing_decisions
            if not d.destination and not d.is_protected and not d.is_allowed_pattern
        )

        print(f"📁 Total Files Analyzed: {total}")
        print(f"🛡️ Protected Files: {protected}")
        print(f"✅ Allowed Patterns: {allowed}")
        print(f"📦 Files to Route: {routed}")
        print(f"❓ Unmatched Files: {unmatched}")

        if routed > 0:
            print("\n🎯 ROUTING DECISIONS:")
            for decision in self.routing_decisions:
                if decision.destination:
                    print(f"   📄 {decision.file_path.name} → {decision.destination}/")

        print(
            f"\n🔍 Mode: {'DRY RUN (no files moved)' if self.dry_run else 'EXECUTE (files will be moved)'}"
        )


def main():
    """Main entry point for the Root Customs Agent."""
    import argparse

    parser = argparse.ArgumentParser(description="Root Customs Agent - Content-Aware Routing")
    parser.add_argument("--execute", action="store_true", help="Execute routing (default: dry-run)")
    parser.add_argument("--project-root", type=str, help="Project root path")

    args = parser.parse_args()

    # Initialize agent
    agent = RootCustomsAgent(
        project_root=Path(args.project_root) if args.project_root else None,
        dry_run=not args.execute,
    )

    # Run inspection
    results = agent.run_inspection()

    print("\n🎉 Root Customs Agent Complete!")
    return results


if __name__ == "__main__":
    main()
