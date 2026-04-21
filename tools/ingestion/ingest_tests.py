#!/usr/bin/env python3
"""
Tests Ingestion for ChromaDB Semantic Memory Layer
Wave 2 Implementation: Structural & Test Intelligence

Ingests test files and guardrail patterns into ChromaDB.
"""

import ast
import hashlib
import logging
import re
import sys
from pathlib import Path

# Add agentic_core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agentic_core"))

from L4_state.client.chroma_client import SovereignChromaClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestsIngestion:
    """
    Ingests test files and guardrail patterns into ChromaDB semantic memory layer.

    Wave 2 focuses on:
    - repo_tests_guardrails: Test files and guardrail patterns
    """

    def __init__(self, repo_root: str, chroma_persist_dir: str = "artifacts/chromadb"):
        """
        Initialize tests ingestion.

        Args:
            repo_root: Repository root directory
            chroma_persist_dir: ChromaDB persistence directory
        """
        self.repo_root = Path(repo_root)

        # Initialize ChromaDB client
        self.chroma = SovereignChromaClient(persist_dir=chroma_persist_dir)

        logger.info("Tests ingestion initialized")

    def ingest_test_files(self) -> int:
        """Ingest test files and their content."""
        logger.info("Starting test files ingestion...")

        documents = []
        metadatas = []
        ids = []

        # Find all test files
        test_patterns = [
            "tests/**/*.py",
            "test_*.py",
            "*_test.py",
            "**/test_*.py",
            "**/*_test.py",
        ]

        test_files = set()
        for pattern in test_patterns:
            test_files.update(self.repo_root.glob(pattern))

        # Also look in specific test directories
        test_dirs = ["tests", "test", "unit_tests", "integration_tests"]
        for test_dir in test_dirs:
            test_path = self.repo_root / test_dir
            if test_path.exists():
                test_files.update(test_path.rglob("*.py"))

        logger.info(f"Found {len(test_files)} test files")

        for file_path in test_files:
            if file_path.name.startswith("."):
                continue

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                if not content.strip():
                    continue

                # Parse test structure
                test_info = self._parse_test_file(content, file_path)

                # Create document content
                doc_content = f"Test file: {file_path.relative_to(self.repo_root)}\n"
                doc_content += f"Test classes: {', '.join(test_info['classes'])}\n"
                doc_content += f"Test functions: {', '.join(test_info['functions'])}\n"
                doc_content += f"Test fixtures: {', '.join(test_info['fixtures'])}\n"
                doc_content += f"Guardrails: {', '.join(test_info['guardrails'])}\n"
                doc_content += f"\nContent:\n{content[:1000]}..."  # First 1000 chars

                # Create metadata (filter out empty lists)
                rel_path = str(file_path.relative_to(self.repo_root))
                metadata = {
                    "object_id": f"urn:agentic:test:{rel_path}",
                    "artifact_type": "test",
                    "file_path": rel_path,
                    "test_type": self._infer_test_type(rel_path),
                    "layer": self._infer_test_layer(rel_path),
                    "subsystem": self._infer_test_subsystem(rel_path),
                    "line_count": len(content.splitlines()),
                    "canonical_digest": hashlib.sha256(content.encode()).hexdigest()[:16],
                }

                # Only add non-empty list fields
                if test_info["classes"]:
                    metadata["test_classes"] = test_info["classes"]
                if test_info["functions"]:
                    metadata["test_functions"] = test_info["functions"]
                if test_info["fixtures"]:
                    metadata["test_fixtures"] = test_info["fixtures"]
                if test_info["guardrails"]:
                    metadata["guardrails"] = test_info["guardrails"]

                documents.append(doc_content)
                metadatas.append(metadata)
                ids.append(f"test_{rel_path.replace('/', '_')}")

            except Exception as e:
                logger.warning(f"Failed to process {file_path}: {e}")

        # Add to ChromaDB in batches
        if documents:
            batch_size = 1000
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i : i + batch_size]
                batch_metas = metadatas[i : i + batch_size]
                batch_ids = ids[i : i + batch_size]

                self.chroma.add_documents(
                    collection_name="repo_tests_guardrails",
                    documents=batch_docs,
                    metadatas=batch_metas,
                    ids=batch_ids,
                )
                logger.info(f"Added batch {i // batch_size + 1}: {len(batch_docs)} test files")

            logger.info(f"Ingested {len(documents)} test files total")

        return len(documents)

    def ingest_guardrail_patterns(self) -> int:
        """Ingest guardrail patterns and validation rules."""
        logger.info("Starting guardrail patterns ingestion...")

        documents = []
        metadatas = []
        ids = []

        # Find guardrail-related files
        guardrail_patterns = [
            "**/guardrail*.py",
            "**/safety*.py",
            "**/validation*.py",
            "**/rules*.py",
            "**/policy*.py",
            "**/constraint*.py",
        ]

        guardrail_files = set()
        for pattern in guardrail_patterns:
            guardrail_files.update(self.repo_root.glob(pattern))

        # Also look in safety and validation directories
        safety_dirs = ["L5_safety", "safety", "validation", "rules", "policy"]
        for safety_dir in safety_dirs:
            safety_path = self.repo_root / "agentic_core" / safety_dir
            if safety_path.exists():
                guardrail_files.update(safety_path.rglob("*.py"))

        logger.info(f"Found {len(guardrail_files)} guardrail-related files")

        for file_path in guardrail_files:
            if file_path.name.startswith("."):
                continue

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                if not content.strip():
                    continue

                # Extract guardrail patterns
                guardrail_info = self._extract_guardrail_patterns(content)

                # Create document content
                doc_content = f"Guardrail file: {file_path.relative_to(self.repo_root)}\n"
                doc_content += f"Guard rules: {len(guardrail_info['rules'])}\n"
                doc_content += f"Validation functions: {len(guardrail_info['validations'])}\n"
                doc_content += f"Constraints: {len(guardrail_info['constraints'])}\n"

                if guardrail_info["rules"]:
                    doc_content += "\nRules:\n"
                    for rule in guardrail_info["rules"][:5]:  # First 5 rules
                        doc_content += f"  - {rule}\n"

                doc_content += f"\nContent:\n{content[:1500]}..."  # First 1500 chars

                # Create metadata (filter out empty lists)
                rel_path = str(file_path.relative_to(self.repo_root))
                metadata = {
                    "object_id": f"urn:agentic:guardrail:{rel_path}",
                    "artifact_type": "guardrail",
                    "file_path": rel_path,
                    "guardrail_type": self._infer_guardrail_type(rel_path),
                    "layer": self._infer_guardrail_layer(rel_path),
                    "rule_count": len(guardrail_info["rules"]),
                    "validation_count": len(guardrail_info["validations"]),
                    "constraint_count": len(guardrail_info["constraints"]),
                    "canonical_digest": hashlib.sha256(content.encode()).hexdigest()[:16],
                }

                # Only add non-empty list fields
                if guardrail_info["rules"]:
                    metadata["rules"] = guardrail_info["rules"]
                if guardrail_info["validations"]:
                    metadata["validations"] = guardrail_info["validations"]
                if guardrail_info["constraints"]:
                    metadata["constraints"] = guardrail_info["constraints"]

                documents.append(doc_content)
                metadatas.append(metadata)
                ids.append(f"guardrail_{rel_path.replace('/', '_')}")

            except Exception as e:
                logger.warning(f"Failed to process {file_path}: {e}")

        # Add to ChromaDB in batches
        if documents:
            batch_size = 500
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i : i + batch_size]
                batch_metas = metadatas[i : i + batch_size]
                batch_ids = ids[i : i + batch_size]

                self.chroma.add_documents(
                    collection_name="repo_tests_guardrails",
                    documents=batch_docs,
                    metadatas=batch_metas,
                    ids=batch_ids,
                )
                logger.info(f"Added guardrail batch {i // batch_size + 1}: {len(batch_docs)} files")

            logger.info(f"Ingested {len(documents)} guardrail files total")

        return len(documents)

    def _parse_test_file(self, content: str, file_path: Path) -> dict[str, list[str]]:
        """Parse test file structure."""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {"classes": [], "functions": [], "fixtures": [], "guardrails": []}

        classes = []
        functions = []
        fixtures = []
        guardrails = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name.startswith("Test") or "test" in node.name.lower():
                    classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                if node.name.startswith("test_") or node.name.startswith("Test"):
                    functions.append(node.name)
                elif "fixture" in node.name.lower() or node.name.startswith("_"):
                    fixtures.append(node.name)

                # Check for guardrail patterns in function names
                if any(
                    keyword in node.name.lower()
                    for keyword in ["guard", "validate", "check", "ensure", "verify"]
                ):
                    guardrails.append(node.name)

        # Also look for guardrail patterns in comments
        guardrail_keywords = ["guardrail", "validation", "constraint", "rule", "policy"]
        for keyword in guardrail_keywords:
            if keyword.lower() in content.lower():
                guardrails.append(keyword)

        return {
            "classes": classes,
            "functions": functions,
            "fixtures": fixtures,
            "guardrails": list(set(guardrails)),  # Remove duplicates
        }

    def _extract_guardrail_patterns(self, content: str) -> dict[str, list[str]]:
        """Extract guardrail patterns from code."""
        rules = []
        validations = []
        constraints = []

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {"rules": [], "validations": [], "constraints": []}

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                name = node.name.lower()

                # Categorize by function name patterns
                if any(keyword in name for keyword in ["rule", "policy", "standard"]):
                    rules.append(node.name)
                elif any(keyword in name for keyword in ["validate", "check", "verify", "ensure"]):
                    validations.append(node.name)
                elif any(keyword in name for keyword in ["constraint", "limit", "bound"]):
                    constraints.append(node.name)

        # Also look for specific patterns in string literals
        for match in re.finditer(
            r'["\']([^"\']*(?:rule|policy|constraint|validation)[^"\']*)["\']', content, re.IGNORECASE
        ):
            pattern = match.group(1)
            if "rule" in pattern.lower():
                rules.append(pattern)
            elif "validation" in pattern.lower():
                validations.append(pattern)
            elif "constraint" in pattern.lower():
                constraints.append(pattern)

        return {
            "rules": list(set(rules)),
            "validations": list(set(validations)),
            "constraints": list(set(constraints)),
        }

    def _infer_test_type(self, file_path: str) -> str:
        """Infer test type from file path."""
        path_lower = file_path.lower()
        if "unit" in path_lower:
            return "unit"
        elif "integration" in path_lower:
            return "integration"
        elif "e2e" in path_lower or "end" in path_lower:
            return "e2e"
        elif "performance" in path_lower:
            return "performance"
        elif "security" in path_lower:
            return "security"
        else:
            return "general"

    def _infer_test_layer(self, file_path: str) -> str:
        """Infer layer from test file path."""
        if "L0" in file_path:
            return "L0"
        elif "L1" in file_path:
            return "L1"
        elif "L2" in file_path:
            return "L2"
        elif "L3" in file_path:
            return "L3"
        elif "L4" in file_path:
            return "L4"
        elif "L5" in file_path:
            return "L5"
        elif "L6" in file_path:
            return "L6"
        else:
            return "unknown"

    def _infer_test_subsystem(self, file_path: str) -> str:
        """Infer subsystem from test file path."""
        path_lower = file_path.lower()
        if "adg" in path_lower:
            return "adg"
        elif "routing" in path_lower:
            return "routing"
        elif "execution" in path_lower:
            return "execution"
        elif "cognition" in path_lower:
            return "cognition"
        elif "state" in path_lower:
            return "state"
        elif "safety" in path_lower:
            return "safety"
        else:
            return "general"

    def _infer_guardrail_type(self, file_path: str) -> str:
        """Infer guardrail type from file path."""
        path_lower = file_path.lower()
        if "guardrail" in path_lower:
            return "guardrail"
        elif "safety" in path_lower:
            return "safety"
        elif "validation" in path_lower:
            return "validation"
        elif "policy" in path_lower:
            return "policy"
        elif "rule" in path_lower:
            return "rule"
        else:
            return "general"

    def _infer_guardrail_layer(self, file_path: str) -> str:
        """Infer layer from guardrail file path."""
        if "L5" in file_path:
            return "L5"
        elif "L0" in file_path:
            return "L0"
        elif "L1" in file_path:
            return "L1"
        elif "L2" in file_path:
            return "L2"
        elif "L3" in file_path:
            return "L3"
        elif "L4" in file_path:
            return "L4"
        elif "L6" in file_path:
            return "L6"
        else:
            return "unknown"

    def run_ingestion(self) -> dict[str, int]:
        """Run complete Wave 2 tests ingestion."""
        logger.info("Starting Wave 2: Tests ingestion...")

        results = {}

        # Ingest test files and guardrails
        results["test_files"] = self.ingest_test_files()
        results["guardrails"] = self.ingest_guardrail_patterns()

        # Log statistics
        logger.info("Wave 2 tests ingestion complete:")
        for category, count in results.items():
            logger.info(f"  {category}: {count} items")

        stats = self.chroma.get_collection_stats("repo_tests_guardrails")
        logger.info(f"Collection 'repo_tests_guardrails': {stats['document_count']} total documents")

        return results


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Wave 2: Tests Ingestion")
    parser.add_argument("--repo-root", default=".", help="Repository root directory")
    parser.add_argument("--chroma-dir", default="artifacts/chromadb", help="ChromaDB persistence directory")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be ingested without actually doing it"
    )
    args = parser.parse_args()

    # Run ingestion
    ingestion = TestsIngestion(
        repo_root=args.repo_root,
        chroma_persist_dir=args.chroma_dir,
    )

    if args.dry_run:
        logger.info("DRY RUN: Would ingest tests and guardrails into ChromaDB")
        return

    results = ingestion.run_ingestion()

    # Summary
    total_items = sum(results.values())
    logger.info(f"Wave 2 complete: {total_items} total test items ingested")


if __name__ == "__main__":
    main()
