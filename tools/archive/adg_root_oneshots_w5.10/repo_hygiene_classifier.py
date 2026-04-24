#!/usr/bin/env python3
"""
Repo Hygiene Classifier - Phase 1 Implementation
Generates JSON manifest for 644 files with classification and reasoning.
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Ensure we can import from agentic_core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

try:
    from tools.utils.planning.token_estimator import ContextWindowEstimator
except ImportError as e:
    logging.error(f"Could not import token estimation utilities: {e}")
    ContextWindowEstimator = None

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class RepoHygieneClassifier:
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.estimator = ContextWindowEstimator()
        self.manifest = []

        # Classification categories
        self.categories = {
            "phase_named": "Scripts named after transient phases (wave*, p0*, phase01*)",
            "root_sprawl": "Capability-named scripts at repo root location",
            "tools_sprawl": "Scripts in wrong tools/ subdirectory",
            "ops_sprawl": "Scripts in wrong ops_scripts/ subdirectory",
            "test_sprawl": "Test files in wrong location",
            "archive_candidate": "Dead-end scripts that should be archived",
            "legitimate": "Properly located and named scripts",
            "config": "Configuration files",
            "documentation": "Documentation files",
        }

    def classify_file(self, file_path: Path) -> dict[str, Any]:
        """Classify a single file and return metadata."""
        relative_path = file_path.relative_to(self.repo_root)
        path_str = str(relative_path)

        # Default classification
        classification = "legitimate"
        reasoning = "Properly located file"

        # Check for phase-named patterns
        if any(pattern in file_path.name for pattern in ["wave", "p0_", "p1_", "p2_", "phase", "Phase"]):
            classification = "phase_named"
            reasoning = "Named after transient phase - encodes when created, not what capability provides"

        # Check for root sprawl
        elif (
            file_path.parent == self.repo_root
            and file_path.suffix == ".py"
            and file_path.name not in ["README.md", ".gitignore"]
        ):
            if any(prefix in file_path.name for prefix in ["analyze", "check", "test", "run", "build"]):
                classification = "root_sprawl"
                reasoning = "Capability-named script at repo root - should be in appropriate subdirectory"

        # Check for tools sprawl
        elif "tools/" in path_str and any(
            pattern in file_path.name for pattern in ["temp", "tmp", "backup", "old", "legacy"]
        ):
            classification = "tools_sprawl"
            reasoning = "Script in tools/ with temporary/legacy naming - should be cleaned up"

        # Check for archive candidates
        elif any(pattern in path_str for pattern in ["archive", "old", "deprecated", "legacy"]):
            classification = "archive_candidate"
            reasoning = "Clearly marked as deprecated or legacy - archive candidate"

        # Configuration files
        elif file_path.suffix in [".yaml", ".yml", ".json", ".toml", ".ini", ".cfg"]:
            classification = "config"
            reasoning = "Configuration file"

        # Documentation
        elif file_path.suffix in [".md", ".rst", ".txt"] or "docs/" in path_str:
            classification = "documentation"
            reasoning = "Documentation file"

        # Get file stats
        try:
            stat = file_path.stat()
            file_size = stat.st_size
            modified_time = datetime.fromtimestamp(stat.st_mtime).isoformat()
        except OSError:
            file_size = 0
            modified_time = "unknown"

        return {
            "path": path_str,
            "classification": classification,
            "reasoning": reasoning,
            "size_bytes": file_size,
            "modified_time": modified_time,
            "category_description": self.categories.get(classification, "Unknown category"),
        }

    def scan_repository(self) -> list[dict[str, Any]]:
        """Scan the entire repository and classify all Python files."""
        logging.info("Starting repository scan...")

        # Look for all .py files first, then add important config/docs
        python_files = list(self.repo_root.rglob("*.py"))
        config_files = []

        # Add important configuration files
        for pattern in ["*.yaml", "*.yml", "*.json", "*.toml", "*.md"]:
            config_files.extend(self.repo_root.rglob(pattern))

        all_files = python_files + config_files
        logging.info(f"Found {len(all_files)} files to classify")

        for file_path in all_files:
            try:
                classification = self.classify_file(file_path)
                self.manifest.append(classification)
            except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
                logging.warning(f"Failed to classify {file_path}: {e}")

        logging.info(f"Successfully classified {len(self.manifest)} files")
        return self.manifest

    def generate_summary_stats(self) -> dict[str, Any]:
        """Generate summary statistics for the manifest."""
        stats = {}
        for classification in self.categories.keys():
            count = len([item for item in self.manifest if item["classification"] == classification])
            stats[classification] = count

        stats["total_files"] = len(self.manifest)
        stats["python_files"] = len([item for item in self.manifest if item["path"].endswith(".py")])
        stats["sprawl_percentage"] = (
            (
                stats.get("phase_named", 0)
                + stats.get("root_sprawl", 0)
                + stats.get("tools_sprawl", 0)
                + stats.get("ops_sprawl", 0)
            )
            / stats["total_files"]
            * 100
        )

        return stats

    def save_manifest(self, output_path: str = "repo_hygiene_manifest.json"):
        """Save the manifest to a JSON file."""
        output_file = self.repo_root / output_path

        manifest_data = {
            "generated_time": datetime.now().isoformat(),
            "repository_root": str(self.repo_root),
            "summary_stats": self.generate_summary_stats(),
            "categories": self.categories,
            "files": self.manifest,
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)

        logging.info(f"Manifest saved to {output_file}")

        # Log summary
        stats = manifest_data["summary_stats"]
        logging.info(f"Summary: {stats['total_files']} total files, {stats['sprawl_percentage']:.1f}% sprawl")

        return output_file


def main():
    """Main execution function."""
    if ContextWindowEstimator is None:
        logging.error("ContextWindowEstimator is required but not available")
        return

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    classifier = RepoHygieneClassifier(repo_root)

    # Scan and classify
    manifest = classifier.scan_repository()

    # Save results
    output_path = classifier.save_manifest("tools/evidence/repo_hygiene_manifest.json")

    # Print token estimate for verification
    manifest_json = json.dumps(classifier.manifest, indent=2)
    estimated_tokens = classifier.estimator._estimate_tokens(manifest_json, "json")
    logging.info(f"Estimated manifest size: {estimated_tokens:,} tokens")

    return output_path, estimated_tokens


if __name__ == "__main__":
    main()
