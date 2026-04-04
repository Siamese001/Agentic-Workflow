#!/usr/bin/env python3
"""
Classify tests into MECE categories: CORE, OPTIONAL, PLATFORM-SPECIFIC, EXTERNAL, EXPERIMENTAL

Classification Rules:
1. CORE - validates primary product functionality, no optional deps
2. OPTIONAL - depends on optional integrations (aws, db, vector db, etc.)
3. PLATFORM-SPECIFIC - OS/GPU/hardware constrained
4. EXTERNAL - requires live services/APIs
5. EXPERIMENTAL - non-production/unstable
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass
class TestClassification:
    file_path: str
    test_name: str
    category: str
    justification: str
    confidence: float  # 0.0-1.0
    markers: list[str]


class TestClassifier:
    """Classify tests into MECE categories based on patterns and heuristics."""

    def __init__(self):
        # Classification patterns
        self.core_patterns = [
            r'test_.*core.*',
            r'test_.*basic.*',
            r'test_.*essential.*',
            r'test_.*required.*',
            r'test_.*fundamental.*',
        ]

        self.optional_patterns = [
            r'test_.*aws.*',
            r'test_.*azure.*',
            r'test_.*gcp.*',
            r'test_.*database.*',
            r'test_.*db.*',
            r'test_.*redis.*',
            r'test_.*vector.*',
            r'test_.*embedding.*',
            r'test_.*openai.*',
            r'test_.*anthropic.*',
            r'test_.*llm.*',
        ]

        self.platform_patterns = [
            r'test_.*windows.*',
            r'test_.*linux.*',
            r'test_.*mac.*',
            r'test_.*gpu.*',
            r'test_.*cuda.*',
            r'test_.*metal.*',
            r'test_.*hardware.*',
        ]

        self.external_patterns = [
            r'test_.*api.*',
            r'test_.*service.*',
            r'test_.*cloud.*',
            r'test_.*remote.*',
            r'test_.*network.*',
            r'test_.*internet.*',
        ]

        self.experimental_patterns = [
            r'test_.*experimental.*',
            r'test_.*beta.*',
            r'test_.*alpha.*',
            r'test_.*prototype.*',
            r'test_.*unstable.*',
        ]

        # File path patterns
        self.core_dirs = {
            'tests/unit/',
            'tests/integration/',
            'tests/adg/',
            'tests/guardian/',
        }

        self.optional_dirs = {
            'tests/optional/',
            'tests/integrations/',
            'tests/cloud/',
            'tests/ai/',
        }

        self.platform_dirs = {
            'tests/platform/',
            'tests/hardware/',
        }

        self.external_dirs = {
            'tests/e2e/',
            'tests/external/',
            'tests/live/',
        }

        self.experimental_dirs = {
            'tests/experimental/',
            'tests/beta/',
        }

    def classify_test(self, test_data: dict[str, Any]) -> TestClassification:
        """Classify a single test."""
        file_path = test_data['file_path']
        test_name = test_data['test_name']
        skip_type = test_data['skip_type']
        dependency = test_data['dependency']
        skip_reason = test_data.get('skip_reason', '')

        # Start with default classification
        category = "CORE"
        justification = "Default classification - validates core functionality"
        confidence = 0.5
        markers = []

        # Check file path patterns first (highest confidence)
        category, justification, confidence = self._classify_by_path(file_path, category, justification, confidence)

        # Check test name patterns
        category, justification, confidence = self._classify_by_name(test_name, category, justification, confidence)

        # Check skip patterns and dependencies
        if skip_type != "none":
            category, justification, confidence = self._classify_by_skip_pattern(
                skip_type, dependency, skip_reason, category, justification, confidence
            )

        # Apply final rules and corrections
        category, justification, confidence = self._apply_final_rules(
            test_data, category, justification, confidence
        )

        return TestClassification(
            file_path=file_path,
            test_name=test_name,
            category=category,
            justification=justification,
            confidence=confidence,
            markers=markers
        )

    def _classify_by_path(self, file_path: str, current_category: str, current_justification: str, current_confidence: float) -> tuple:
        """Classify based on file path."""
        for pattern in self.experimental_dirs:
            if pattern in file_path:
                return "EXPERIMENTAL", f"In experimental directory: {pattern}", 0.9

        for pattern in self.external_dirs:
            if pattern in file_path:
                return "EXTERNAL", f"In external directory: {pattern}", 0.9

        for pattern in self.platform_dirs:
            if pattern in file_path:
                return "PLATFORM-SPECIFIC", f"In platform directory: {pattern}", 0.9

        for pattern in self.optional_dirs:
            if pattern in file_path:
                return "OPTIONAL", f"In optional directory: {pattern}", 0.9

        for pattern in self.core_dirs:
            if pattern in file_path:
                return "CORE", f"In core directory: {pattern}", 0.9

        # Archives and backups are typically not core
        if 'archives/' in file_path or '.backup/' in file_path:
            return "EXPERIMENTAL", "In archive/backup directory", 0.8

        return current_category, current_justification, current_confidence

    def _classify_by_name(self, test_name: str, current_category: str, current_justification: str, current_confidence: float) -> tuple:
        """Classify based on test name patterns."""
        # Experimental patterns (highest priority)
        for pattern in self.experimental_patterns:
            if re.match(pattern, test_name, re.IGNORECASE):
                return "EXPERIMENTAL", f"Experimental test name pattern: {pattern}", 0.8

        # External patterns
        for pattern in self.external_patterns:
            if re.match(pattern, test_name, re.IGNORECASE):
                return "EXTERNAL", f"External test name pattern: {pattern}", 0.8

        # Platform patterns
        for pattern in self.platform_patterns:
            if re.match(pattern, test_name, re.IGNORECASE):
                return "PLATFORM-SPECIFIC", f"Platform test name pattern: {pattern}", 0.8

        # Optional patterns
        for pattern in self.optional_patterns:
            if re.match(pattern, test_name, re.IGNORECASE):
                return "OPTIONAL", f"Optional test name pattern: {pattern}", 0.8

        # Core patterns
        for pattern in self.core_patterns:
            if re.match(pattern, test_name, re.IGNORECASE):
                return "CORE", f"Core test name pattern: {pattern}", 0.7

        return current_category, current_justification, current_confidence

    def _classify_by_skip_pattern(self, skip_type: str, dependency: str, skip_reason: str,
                                 current_category: str, current_justification: str, current_confidence: float) -> tuple:
        """Classify based on skip patterns and dependencies."""
        if skip_type == "import_error":
            # ImportError skips suggest optional dependencies
            if self._is_optional_dependency(dependency):
                return "OPTIONAL", f"Optional dependency: {dependency}", 0.8
            elif self._is_platform_dependency(dependency):
                return "PLATFORM-SPECIFIC", f"Platform dependency: {dependency}", 0.8
            elif self._is_external_dependency(dependency):
                return "EXTERNAL", f"External dependency: {dependency}", 0.8
            else:
                # Unknown dependency - assume optional
                return "OPTIONAL", f"Unknown dependency treated as optional: {dependency}", 0.6

        elif skip_type == "runtime_condition":
            # Runtime skips often indicate platform or external dependencies
            if any(keyword in skip_reason.lower() for keyword in ['gpu', 'cuda', 'windows', 'linux', 'mac']):
                return "PLATFORM-SPECIFIC", f"Platform condition: {skip_reason}", 0.7
            elif any(keyword in skip_reason.lower() for keyword in ['api', 'service', 'network', 'internet']):
                return "EXTERNAL", f"External condition: {skip_reason}", 0.7
            else:
                return "OPTIONAL", f"Runtime condition treated as optional: {skip_reason}", 0.6

        return current_category, current_justification, current_confidence

    def _apply_final_rules(self, test_data: dict[str, Any], current_category: str,
                          current_justification: str, current_confidence: float) -> tuple:
        """Apply final classification rules and corrections."""
        file_path = test_data['file_path']

        # Unit tests are typically core unless they clearly depend on external services
        if '/unit/' in file_path and current_confidence < 0.8:
            return "CORE", "Unit test - assumed core functionality", 0.7

        # Tests in archives are experimental
        if 'archives/' in file_path:
            return "EXPERIMENTAL", "Test in archive directory", 0.9

        # Tests with high confidence classifications stand
        if current_confidence >= 0.8:
            return current_category, current_justification, current_confidence

        # Low confidence tests - analyze more deeply
        return self._deep_classify(test_data, current_category, current_justification, current_confidence)

    def _deep_classify(self, test_data: dict[str, Any], current_category: str,
                       current_justification: str, current_confidence: float) -> tuple:
        """Deep classification for low-confidence tests."""
        file_path = test_data['file_path']
        test_name = test_data['test_name']

        # Check if test validates core agentic functionality
        core_keywords = [
            'agent', 'routing', 'policy', 'safety', 'guardrail', 'execution',
            'adg', 'determinism', 'sovereignty', 'layer'
        ]

        if any(keyword in test_name.lower() for keyword in core_keywords):
            return "CORE", f"Core functionality keyword: {test_name}", 0.7

        # Check if test is in core agentic_core directories
        if 'agentic_core/' in file_path and '/tests/' in file_path:
            return "CORE", "Test in agentic_core directory", 0.7

        # Default to optional for uncertain cases
        return "OPTIONAL", "Uncertain classification - default to optional", 0.4

    def _is_optional_dependency(self, dependency: str) -> bool:
        """Check if dependency is optional."""
        optional_deps = [
            'torch', 'transformers', 'openai', 'anthropic', 'boto3', 'redis',
            'postgresql', 'mysql', 'mongodb', 'elasticsearch', 'chromadb',
            'pinecone', 'weaviate', 'faiss', 'numpy', 'pandas', 'matplotlib'
        ]
        return any(dep in dependency.lower() for dep in optional_deps)

    def _is_platform_dependency(self, dependency: str) -> bool:
        """Check if dependency is platform-specific."""
        platform_deps = [
            'torch.cuda', 'tensorflow', 'cupy', 'numba', 'windows', 'linux',
            'macos', 'darwin', 'win32'
        ]
        return any(dep in dependency.lower() for dep in platform_deps)

    def _is_external_dependency(self, dependency: str) -> bool:
        """Check if dependency requires external services."""
        external_deps = [
            'requests', 'httpx', 'aiohttp', 'boto3', 'google-cloud', 'azure',
            'aws', 'api', 'service', 'remote'
        ]
        return any(dep in dependency.lower() for dep in external_deps)


def classify_all_tests() -> dict[str, Any]:
    """Classify all tests in the inventory."""
    print("🏷️  Classifying tests into MECE categories...")

    # Load inventory
    with open('tools/test_enforcement/test_inventory.json') as f:
        inventory = json.load(f)

    classifier = TestClassifier()
    classifications = []

    for test_data in inventory['tests']:
        classification = classifier.classify_test(test_data)
        classifications.append({
            'file_path': classification.file_path,
            'test_name': classification.test_name,
            'category': classification.category,
            'justification': classification.justification,
            'confidence': classification.confidence,
            'markers': classification.markers
        })

    # Build classification result
    result = {
        "metadata": {
            "classification_timestamp": "2026-03-24T18:31:00Z",
            "total_tests_classified": len(classifications),
            "classifier_version": "1.0"
        },
        "classifications": classifications
    }

    # Add summary statistics
    category_counts = {}
    confidence_counts = {"high": 0, "medium": 0, "low": 0}

    for classification in classifications:
        category = classification['category']
        confidence = classification['confidence']

        category_counts[category] = category_counts.get(category, 0) + 1

        if confidence >= 0.8:
            confidence_counts["high"] += 1
        elif confidence >= 0.6:
            confidence_counts["medium"] += 1
        else:
            confidence_counts["low"] += 1

    result["summary"] = {
        "categories": category_counts,
        "confidence_distribution": confidence_counts
    }

    return result


def main():
    """Main entry point."""
    print("=" * 80)
    print("TEST CLASSIFICATION ENGINE")
    print("=" * 80)

    classification_result = classify_all_tests()

    # Write classifications to file
    output_dir = PROJECT_ROOT / "tools" / "test_enforcement"
    classification_file = output_dir / "test_classification.json"

    with open(classification_file, 'w', encoding='utf-8') as f:
        json.dump(classification_result, f, indent=2, sort_keys=True)

    print(f"✅ Classifications written to: {classification_file}")

    # Print summary
    summary = classification_result["summary"]
    print("\n📊 CLASSIFICATION SUMMARY:")
    print(f"  Total tests classified: {classification_result['metadata']['total_tests_classified']}")

    print("\nCategories:")
    for category, count in sorted(summary["categories"].items()):
        percentage = (count / classification_result['metadata']['total_tests_classified']) * 100
        print(f"  {category}: {count} ({percentage:.1f}%)")

    print("\nConfidence distribution:")
    for level, count in summary["confidence_distribution"].items():
        percentage = (count / classification_result['metadata']['total_tests_classified']) * 100
        print(f"  {level}: {count} ({percentage:.1f}%)")

    print("\n" + "=" * 80)
    print("NEXT STEP: Identify violations and refactor tests")
    print("=" * 80)


if __name__ == "__main__":
    main()
