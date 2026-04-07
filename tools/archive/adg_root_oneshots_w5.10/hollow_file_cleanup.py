#!/usr/bin/env python3
"""
Hollow File Batch Cleanup Scanner

ADG-powered cleanup analysis for hollow files.
Generates prioritized cleanup manifests based on import dependencies.
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_core.L5_safety.validators.hollow_file_detector_validator import (
    BehavioralNodeCounter,
    HollowFileDetector,
)


@dataclass
class CleanupManifest:
    """Manifest for hollow file cleanup operations."""
    tier1_safe_delete: list[str] = field(default_factory=list)  # No incoming edges
    tier2_boilerplate_only: list[str] = field(default_factory=list)  # Only boilerplate imports
    tier3_behavioral_imports: list[str] = field(default_factory=list)  # Has behavioral imports
    metadata: dict[str, dict] = field(default_factory=dict)


@dataclass
class FileAnalysis:
    """Analysis result for a single file."""
    file_path: str
    is_hollow: bool
    classification: str
    behavioral_nodes: int
    boilerplate_nodes: int
    incoming_edges: list[str]
    outgoing_edges: list[str]
    incoming_count: int
    outgoing_count: int


class HollowFileCleanupAnalyzer:
    """Analyzes hollow files and generates cleanup manifests."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.detector = HollowFileDetector()

    def analyze_file(self, file_path: Path) -> FileAnalysis:
        """Analyze a single file for hollow classification and dependencies."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            content = ""

        # Parse AST
        try:
            import ast
            tree = ast.parse(content)
        except SyntaxError:
            tree = None

        # Detect hollow status
        violations = self.detector.detect(file_path, tree) if tree else []
        is_hollow = len(violations) > 0
        classification = violations[0].metadata.get("classification", "healthy") if violations else "healthy"

        # Count nodes
        if tree:
            counter = BehavioralNodeCounter()
            counter.visit(tree)
            behavioral_nodes = counter.behavioral_functions + counter.behavioral_classes
            boilerplate_nodes = counter.import_statements + counter.boilerplate_statements
        else:
            behavioral_nodes = 0
            boilerplate_nodes = 0

        # Analyze imports (simplified version without ADG)
        incoming_edges, outgoing_edges = self._analyze_imports(content, str(file_path))

        return FileAnalysis(
            file_path=str(file_path),
            is_hollow=is_hollow,
            classification=classification,
            behavioral_nodes=behavioral_nodes,
            boilerplate_nodes=boilerplate_nodes,
            incoming_edges=incoming_edges,
            outgoing_edges=outgoing_edges,
            incoming_count=len(incoming_edges),
            outgoing_count=len(outgoing_edges),
        )

    def _analyze_imports(self, content: str, file_path: str) -> tuple[list[str], list[str]]:
        """Simple import analysis without ADG dependency."""
        import ast

        incoming: list[str] = []
        outgoing: list[str] = []

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return incoming, outgoing

        # Find outgoing imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    outgoing.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    outgoing.append(node.module)

        # For incoming analysis, we'd normally query ADG
        # For now, return empty list (will be populated by ADG if available)

        return incoming, outgoing

    def scan_repository(self) -> list[FileAnalysis]:
        """Scan entire repository for hollow files."""
        results = []

        # Find all Python files
        python_files = list(self.repo_root.rglob("*.py"))

        # Exclude common non-source directories
        python_files = [
            f for f in python_files
            if not any(part.startswith(('.', '__')) for part in f.parts)
            and "site-packages" not in str(f)
        ]

        for file_path in python_files:
            try:
                analysis = self.analyze_file(file_path)
            except StopIteration:
                # Skip this file and continue with next
                continue
            if analysis.is_hollow:
                results.append(analysis)

        return results

    def classify_cleanup_safety(self, analyses: list[FileAnalysis]) -> CleanupManifest:
        """Classify hollow files by cleanup safety."""
        manifest = CleanupManifest()

        for analysis in analyses:
            rel_path = str(Path(analysis.file_path).relative_to(self.repo_root))

            # Store metadata
            manifest.metadata[rel_path] = {
                "classification": analysis.classification,
                "behavioral_nodes": analysis.behavioral_nodes,
                "boilerplate_nodes": analysis.boilerplate_nodes,
                "incoming_count": analysis.incoming_count,
                "outgoing_count": analysis.outgoing_count,
                "incoming_edges": analysis.incoming_edges,
                "outgoing_edges": analysis.outgoing_edges,
            }

            # Classify by safety
            if analysis.incoming_count == 0 and analysis.outgoing_count == 0:
                manifest.tier1_safe_delete.append(rel_path)
            elif analysis.incoming_count == 0:
                # Only imports, no exports - likely boilerplate only
                manifest.tier2_boilerplate_only.append(rel_path)
            else:
                # Has both imports and exports - behavioral dependencies
                manifest.tier3_behavioral_imports.append(rel_path)

        return manifest

    def try_adg_enhancement(self, manifest: CleanupManifest) -> CleanupManifest:
        """Try to enhance with ADG data if available."""
        try:
            # Try to import ADG components
            from agentic_core.adg.artifact.builder_types import ADGArtifactBuilder
            from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

            print("🔍 ADG available - enhancing with dependency analysis...")

            # Quick scan for hollow files
            scanner = ADGStaticScanner(repo_root=self.repo_root)
            result = scanner.scan()

            # Build artifact for analysis
            builder = ADGArtifactBuilder(repo_root=self.repo_root)
            artifact = builder.build(result)

            # Enhance manifest with ADG data
            for file_path in list(manifest.metadata.keys()):
                incoming = []

                # Count incoming edges from ADG
                for edge in artifact.relations:
                    if edge.to_name.endswith(file_path):
                        incoming.append(edge.from_name)

                # Update metadata
                manifest.metadata[file_path]["incoming_edges"] = incoming
                manifest.metadata[file_path]["incoming_count"] = len(incoming)

                # Re-classify if needed
                if len(incoming) == 0:
                    if file_path not in manifest.tier1_safe_delete:
                        if file_path in manifest.tier2_boilerplate_only:
                            manifest.tier2_boilerplate_only.remove(file_path)
                        elif file_path in manifest.tier3_behavioral_imports:
                            manifest.tier3_behavioral_imports.remove(file_path)
                        manifest.tier1_safe_delete.append(file_path)

            print("✅ ADG enhancement complete")

        except ImportError:
            print("⚠️  ADG not available - using basic import analysis only")
        except Exception as e:
            print(f"⚠️  ADG enhancement failed: {e}")

        return manifest


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate hollow file cleanup manifest")
    parser.add_argument("--output", "-o", type=Path, help="Output JSON file")
    parser.add_argument("--repo", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Initialize analyzer
    analyzer = HollowFileCleanupAnalyzer(args.repo)

    # Scan repository
    print("🔍 Scanning repository for hollow files...")
    analyses = analyzer.scan_repository()

    if not analyses:
        print("✅ No hollow files found")
        return 0

    print(f"📊 Found {len(analyses)} hollow files")

    # Generate manifest
    print("📋 Generating cleanup manifest...")
    manifest = analyzer.classify_cleanup_safety(analyses)

    # Try ADG enhancement
    manifest = analyzer.try_adg_enhancement(manifest)

    # Display summary
    print("\n📈 Cleanup Summary:")
    print(f"  Tier 1 (Safe to delete): {len(manifest.tier1_safe_delete)} files")
    print(f"  Tier 2 (Boilerplate only): {len(manifest.tier2_boilerplate_only)} files")
    print(f"  Tier 3 (Has behavioral imports): {len(manifest.tier3_behavioral_imports)} files")

    if args.verbose:
        print("\n📄 Detailed Results:")
        for tier, files in [
            ("Tier 1 - Safe Delete", manifest.tier1_safe_delete),
            ("Tier 2 - Boilerplate Only", manifest.tier2_boilerplate_only),
            ("Tier 3 - Behavioral Imports", manifest.tier3_behavioral_imports),
        ]:
            if files:
                print(f"\n{tier}:")
                for f in sorted(files):
                    meta = manifest.metadata[f]
                    print(f"  {f} (incoming: {meta['incoming_count']}, outgoing: {meta['outgoing_count']})")

    # Write output
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)

        output_data = {
            "summary": {
                "total_hollow_files": len(analyses),
                "tier1_safe_delete": len(manifest.tier1_safe_delete),
                "tier2_boilerplate_only": len(manifest.tier2_boilerplate_only),
                "tier3_behavioral_imports": len(manifest.tier3_behavioral_imports),
            },
            "manifest": {
                "tier1_safe_delete": manifest.tier1_safe_delete,
                "tier2_boilerplate_only": manifest.tier2_boilerplate_only,
                "tier3_behavioral_imports": manifest.tier3_behavioral_imports,
            },
            "metadata": manifest.metadata,
        }

        args.output.write_text(json.dumps(output_data, indent=2))
        print(f"\n💾 Manifest written to {args.output}")

    # Generate cleanup commands
    if manifest.tier1_safe_delete:
        print("\n🧹 Suggested cleanup commands for Tier 1 files:")
        for f in manifest.tier1_safe_delete:
            print(f"  git rm {f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
