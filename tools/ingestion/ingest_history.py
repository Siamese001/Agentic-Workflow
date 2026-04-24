#!/usr/bin/env python3
"""
History Ingestion for ChromaDB Semantic Memory Layer
Wave 3 Implementation: Execution & History Intelligence

Ingests git history and incident RCA data into ChromaDB.
"""

import hashlib
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import chromadb

# Add agentic_core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_core.L4_state.utils.client.chroma_client import SovereignChromaClient
from agentic_core.L4_state.config.chroma_paths import canonical_persist_dir_str

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HistoryIngestion:
    """
    Ingests git history and incident RCA data into ChromaDB semantic memory layer.

    Wave 3 focuses on:
    - repo_git_history: Git commit history and changes
    - repo_incidents_rca: Incident reports and root cause analysis
    """

    def __init__(self, repo_root: str, chroma_persist_dir: str = canonical_persist_dir_str()):
        """
        Initialize history ingestion.

        Args:
            repo_root: Repository root directory
            chroma_persist_dir: ChromaDB persistence directory
        """
        self.repo_root = Path(repo_root)

        # Initialize ChromaDB client
        self.chroma = SovereignChromaClient(persist_dir=chroma_persist_dir)

        logger.info("History ingestion initialized")

    def ingest_git_history(self) -> int:
        """Ingest git commit history."""
        logger.info("Starting git history ingestion...")

        documents = []
        metadatas = []
        ids = []

        try:
            # Get git log
            git_log_cmd = [
                "git",
                "log",
                "--pretty=format:%H|%an|%ad|%s|%b",
                "--date=iso",
                "--name-only",
                "-1000",  # Last 1000 commits
            ]

            result = subprocess.run(
                git_log_cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=60,
            )

            if result.returncode != 0:
                logger.warning(f"Failed to get git log: {result.stderr}")
                return 0

            log_output = result.stdout
            commits = self._parse_git_log(log_output)

            logger.info(f"Parsed {len(commits)} commits")

            for commit in commits:
                # Create document content
                doc_content = f"Git commit: {commit['hash']}\n"
                doc_content += f"Author: {commit['author']}\n"
                doc_content += f"Date: {commit['date']}\n"
                doc_content += f"Subject: {commit['subject']}\n"
                doc_content += f"Files changed: {len(commit['files'])}\n"
                doc_content += f"File types: {', '.join(commit['file_types'])}\n"

                if commit["components"]:
                    doc_content += f"Components: {', '.join(commit['components'])}\n"

                if commit["layers"]:
                    doc_content += f"Layers: {', '.join(commit['layers'])}\n"

                doc_content += f"\nMessage:\n{commit['body'][:500]}..."

                # Create metadata
                metadata = {
                    "object_id": f"urn:agentic:git:{commit['hash']}",
                    "artifact_type": "git_commit",
                    "commit_hash": commit["hash"],
                    "author": commit["author"],
                    "date": commit["date"],
                    "subject": commit["subject"],
                    "files_changed": len(commit["files"]),
                    "file_types": commit["file_types"],
                    "components": commit["components"],
                    "layers": commit["layers"],
                    "canonical_digest": hashlib.sha256(commit["hash"].encode()).hexdigest()[:16],
                }

                # Only add non-empty list fields
                if commit["files"]:
                    metadata["files"] = commit["files"][:20]  # Limit to first 20 files
                if commit["body"]:
                    metadata["body"] = commit["body"][:1000]  # Limit body length

                documents.append(doc_content)
                metadatas.append(metadata)
                ids.append(f"git_{commit['hash']}")

        except Exception as e:
            logger.error(f"Failed to ingest git history: {e}")
            return 0

        # Add to ChromaDB in smaller batches to avoid compaction issues
        if documents:
            batch_size = 100  # Smaller batch size
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i : i + batch_size]
                batch_metas = metadatas[i : i + batch_size]
                batch_ids = ids[i : i + batch_size]

                try:
                    self.chroma.add_documents(
                        collection_name="repo_git_history",
                        documents=batch_docs,
                        metadatas=batch_metas,
                        ids=batch_ids,
                    )
                    logger.info(f"Added batch {i // batch_size + 1}: {len(batch_docs)} commits")
                except Exception as e:
                    logger.error(f"Failed to add batch {i // batch_size + 1}: {e}")
                    continue

            logger.info(f"Ingested {len(documents)} git commits total")

        return len(documents)

    def ingest_incident_rca(self) -> int:
        """Ingest incident reports and RCA data."""
        logger.info("Starting incident RCA ingestion...")

        documents = []
        metadatas = []
        ids = []

        # Look for incident and RCA files
        incident_patterns = [
            "**/RCA_*.md",
            "**/incident_*.md",
            "**/incident_*.json",
            "**/rca_*.md",
            "**/*incident*.md",
            "**/*rca*.md",
        ]

        incident_files = set()
        for pattern in incident_patterns:
            incident_files.update(self.repo_root.glob(pattern))

        # Also look in specific directories
        incident_dirs = [
            "docs/reports/plans",  # RCA plans are stored here
            "incidents",
            "rca",
            "postmortem",
        ]

        for incident_dir in incident_dirs:
            incident_path = self.repo_root / incident_dir
            if incident_path.exists():
                incident_files.update(incident_path.rglob("*.md"))
                incident_files.update(incident_path.rglob("*.json"))

        logger.info(f"Found {len(incident_files)} incident/RCA files")

        for file_path in incident_files:
            if file_path.name.startswith("."):
                continue

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                if not content.strip():
                    continue

                # Parse incident information
                incident_info = self._parse_incident_rca(content, file_path)

                # Create document content
                doc_content = f"Incident RCA: {file_path.relative_to(self.repo_root)}\n"
                doc_content += f"Type: {incident_info['type']}\n"
                doc_content += f"Severity: {incident_info['severity']}\n"
                doc_content += f"Date: {incident_info['date']}\n"
                doc_content += f"Status: {incident_info['status']}\n"

                if incident_info["components"]:
                    doc_content += f"Components: {', '.join(incident_info['components'])}\n"

                if incident_info["layers"]:
                    doc_content += f"Layers: {', '.join(incident_info['layers'])}\n"

                if incident_info["root_causes"]:
                    doc_content += f"Root causes: {len(incident_info['root_causes'])}\n"

                if incident_info["symptoms"]:
                    doc_content += f"Symptoms: {len(incident_info['symptoms'])}\n"

                doc_content += f"\nContent:\n{content[:1500]}..."

                # Create metadata
                rel_path = str(file_path.relative_to(self.repo_root))
                metadata = {
                    "object_id": f"urn:agentic:incident:{rel_path}",
                    "artifact_type": "incident_rca",
                    "file_path": rel_path,
                    "incident_type": incident_info["type"],
                    "severity": incident_info["severity"],
                    "date": incident_info["date"],
                    "status": incident_info["status"],
                    "components": incident_info["components"],
                    "layers": incident_info["layers"],
                    "root_cause_count": len(incident_info["root_causes"]),
                    "symptom_count": len(incident_info["symptoms"]),
                    "file_size": len(content),
                    "canonical_digest": hashlib.sha256(content.encode()).hexdigest()[:16],
                }

                # Only add non-empty list fields
                if incident_info["root_causes"]:
                    metadata["root_causes"] = incident_info["root_causes"]
                if incident_info["symptoms"]:
                    metadata["symptoms"] = incident_info["symptoms"]
                if incident_info["fixes"]:
                    metadata["fixes"] = incident_info["fixes"]

                documents.append(doc_content)
                metadatas.append(metadata)
                ids.append(f"incident_{rel_path.replace('/', '_')}")

            except Exception as e:
                logger.warning(f"Failed to process {file_path}: {e}")

        # Add to ChromaDB in smaller batches to avoid compaction issues
        if documents:
            batch_size = 100  # Smaller batch size
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i : i + batch_size]
                batch_metas = metadatas[i : i + batch_size]
                batch_ids = ids[i : i + batch_size]

                try:
                    self.chroma.add_documents(
                        collection_name="repo_incidents_rca",
                        documents=batch_docs,
                        metadatas=batch_metas,
                        ids=batch_ids,
                    )
                    logger.info(f"Added batch {i // batch_size + 1}: {len(batch_docs)} incidents")
                except Exception as e:
                    logger.error(f"Failed to add batch {i // batch_size + 1}: {e}")
                    continue

            logger.info(f"Ingested {len(documents)} incident RCA files total")

        return len(documents)

    def ingest_synthetic_incidents(self) -> int:
        """Generate synthetic incidents for testing failure clustering."""
        logger.info("Starting synthetic incidents generation...")

        documents = []
        metadatas = []
        ids = []

        # Synthetic incident scenarios
        synthetic_incidents = [
            {
                "name": "UWG Write Failure",
                "type": "runtime_failure",
                "severity": "high",
                "components": ["UniversalWriteGateway", "ADG"],
                "layers": ["L2", "L4"],
                "root_causes": ["Memory exhaustion", "Connection timeout"],
                "symptoms": ["Write operations failing", "Increased latency"],
                "fixes": ["Increased memory limits", "Connection pooling"],
            },
            {
                "name": "ADG Scanner Timeout",
                "type": "performance_issue",
                "severity": "medium",
                "components": ["StaticScanner", "SQLite"],
                "layers": ["L4"],
                "root_causes": ["Large codebase", "Inefficient queries"],
                "symptoms": ["Scan timeouts", "High CPU usage"],
                "fixes": ["Query optimization", "Incremental scanning"],
            },
            {
                "name": "L0 Routing Deadlock",
                "type": "concurrency_issue",
                "severity": "high",
                "components": ["Router", "Policy"],
                "layers": ["L0", "L5"],
                "root_causes": ["Lock contention", "Circular dependency"],
                "symptoms": ["Request hanging", "System freeze"],
                "fixes": ["Lock reordering", "Dependency injection"],
            },
            {
                "name": "L1 Cognition Memory Leak",
                "type": "memory_leak",
                "severity": "medium",
                "components": ["SemanticRetriever", "ChromaDB"],
                "layers": ["L1", "L4"],
                "root_causes": ["Unclosed connections", "Cache not cleared"],
                "symptoms": ["Memory growth", "Performance degradation"],
                "fixes": ["Connection management", "Cache cleanup"],
            },
            {
                "name": "L5 Safety False Positives",
                "type": "logic_error",
                "severity": "low",
                "components": ["Guardrails", "Validation"],
                "layers": ["L5"],
                "root_causes": ["Incorrect thresholds", "Rule conflicts"],
                "symptoms": ["False rejections", "User complaints"],
                "fixes": ["Threshold tuning", "Rule prioritization"],
            },
        ]

        # Generate variations to reach 100+ incidents for clustering
        for i in range(120):  # 120 synthetic incidents
            base_incident = synthetic_incidents[i % len(synthetic_incidents)]

            # Create variation
            timestamp = datetime.now().isoformat()
            severity_variation = self._vary_severity(base_incident["severity"], i)

            doc_content = f"Synthetic incident: {base_incident['name']} (variant {i})\n"
            doc_content += f"Type: {base_incident['type']}\n"
            doc_content += f"Severity: {severity_variation}\n"
            doc_content += f"Date: {timestamp}\n"
            doc_content += "Status: resolved\n"
            doc_content += f"Components: {', '.join(base_incident['components'])}\n"
            doc_content += f"Layers: {', '.join(base_incident['layers'])}\n"
            doc_content += f"Root causes: {', '.join(base_incident['root_causes'])}\n"
            doc_content += f"Symptoms: {', '.join(base_incident['symptoms'])}\n"
            doc_content += f"Fixes: {', '.join(base_incident['fixes'])}\n"

            # Add variation details
            doc_content += "\nIncident Details:\n"
            doc_content += f"  Variant ID: {i}\n"
            doc_content += f"  Base scenario: {i % len(synthetic_incidents)}\n"
            doc_content += f"  Impact score: {i * 2 + 10}\n"

            metadata = {
                "object_id": f"urn:agentic:synthetic:incident_{i}",
                "artifact_type": "synthetic_incident",
                "incident_name": f"{base_incident['name']} (variant {i})",
                "incident_type": base_incident["type"],
                "severity": severity_variation,
                "date": timestamp,
                "status": "resolved",
                "components": base_incident["components"],
                "layers": base_incident["layers"],
                "root_causes": base_incident["root_causes"],
                "symptoms": base_incident["symptoms"],
                "fixes": base_incident["fixes"],
                "synthetic": True,
                "variant": i,
                "base_scenario": i % len(synthetic_incidents),
                "impact_score": i * 2 + 10,
                "canonical_digest": hashlib.sha256(doc_content.encode()).hexdigest()[:16],
            }

            documents.append(doc_content)
            metadatas.append(metadata)
            ids.append(f"synthetic_incident_{i}")

        # Add to ChromaDB in smaller batches to avoid compaction issues
        if documents:
            batch_size = 100  # Smaller batch size
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i : i + batch_size]
                batch_metas = metadatas[i : i + batch_size]
                batch_ids = ids[i : i + batch_size]

                try:
                    self.chroma.add_documents(
                        collection_name="repo_incidents_rca",
                        documents=batch_docs,
                        metadatas=batch_metas,
                        ids=batch_ids,
                    )
                    logger.info(f"Added synthetic batch {i // batch_size + 1}: {len(batch_docs)} incidents")
                except Exception as e:
                    logger.error(f"Failed to add synthetic batch {i // batch_size + 1}: {e}")
                    continue

            logger.info(f"Ingested {len(documents)} synthetic incidents total")

        return len(documents)

    def _parse_git_log(self, log_output: str) -> list[dict[str, Any]]:
        """Parse git log output into structured commits."""
        commits = []
        current_commit = None
        parsing_files = False

        for line in log_output.split("\n"):
            if not line.strip():
                continue

            if "|" in line and not parsing_files:
                # New commit
                if current_commit:
                    commits.append(current_commit)

                parts = line.split("|", 4)
                if len(parts) >= 4:
                    current_commit = {
                        "hash": parts[0],
                        "author": parts[1],
                        "date": parts[2],
                        "subject": parts[3],
                        "body": parts[4] if len(parts) > 4 else "",
                        "files": [],
                        "file_types": [],
                        "components": [],
                        "layers": [],
                    }
                parsing_files = False

            elif current_commit and line.startswith("    "):
                # Commit body continuation
                current_commit["body"] += line.strip() + "\n"

            elif current_commit and not line.startswith("    ") and line.strip():
                # File list starts
                parsing_files = True
                file_path = line.strip()
                current_commit["files"].append(file_path)

                # Extract file type
                if "." in file_path:
                    file_ext = file_path.split(".")[-1]
                    current_commit["file_types"].append(file_ext)

                # Extract components and layers from path
                path_parts = file_path.split("/")

                # Layer detection
                for part in path_parts:
                    if part.startswith("L") and part[1:].isdigit():
                        current_commit["layers"].append(part)

                # Component detection
                for component in [
                    "UWG",
                    "ADG",
                    "Scanner",
                    "Router",
                    "Gateway",
                    "Agent",
                    "Orchestrator",
                    "Guardrail",
                ]:
                    if component.lower() in file_path.lower():
                        current_commit["components"].append(component)

        # Add last commit
        if current_commit:
            commits.append(current_commit)

        return commits

    def _parse_incident_rca(self, content: str, file_path: Path) -> dict[str, Any]:
        """Parse incident RCA from file content."""
        incident_info = {
            "type": "unknown",
            "severity": "unknown",
            "date": datetime.now().isoformat(),
            "status": "unknown",
            "components": [],
            "layers": [],
            "root_causes": [],
            "symptoms": [],
            "fixes": [],
        }

        # Extract from filename first
        filename = file_path.name.lower()

        if "rca" in filename:
            incident_info["type"] = "rca"
        elif "incident" in filename:
            incident_info["type"] = "incident"

        # Parse content for key information
        lines = content.split("\n")
        current_section = None

        for line in lines:
            line_lower = line.lower().strip()

            # Detect sections
            if any(keyword in line_lower for keyword in ["root cause", "cause", "why"]):
                current_section = "root_causes"
            elif any(keyword in line_lower for keyword in ["symptom", "symptom", "what", "observation"]):
                current_section = "symptoms"
            elif any(keyword in line_lower for keyword in ["fix", "solution", "resolution", "action"]):
                current_section = "fixes"
            elif line_lower.startswith("#") or line_lower.startswith("##"):
                current_section = None

            # Extract severity
            if any(keyword in line_lower for keyword in ["critical", "high", "severe"]):
                incident_info["severity"] = "high"
            elif any(keyword in line_lower for keyword in ["medium", "moderate"]):
                incident_info["severity"] = "medium"
            elif any(keyword in line_lower for keyword in ["low", "minor"]):
                incident_info["severity"] = "low"

            # Extract date
            import re

            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", line)
            if date_match:
                incident_info["date"] = date_match.group(1)

            # Extract components
            for component in [
                "UWG",
                "ADG",
                "Scanner",
                "Router",
                "Gateway",
                "Agent",
                "Orchestrator",
                "Guardrail",
            ]:
                if component.lower() in line_lower:
                    incident_info["components"].append(component)

            # Extract layers
            layer_match = re.search(r"L[0-6]", line)
            if layer_match:
                incident_info["layers"].append(layer_match.group())

            # Extract section content
            if current_section and line.strip() and not line.startswith("#"):
                if current_section == "root_causes":
                    if line.strip() and len(line.strip()) > 5:
                        incident_info["root_causes"].append(line.strip())
                elif current_section == "symptoms":
                    if line.strip() and len(line.strip()) > 5:
                        incident_info["symptoms"].append(line.strip())
                elif current_section == "fixes":
                    if line.strip() and len(line.strip()) > 5:
                        incident_info["fixes"].append(line.strip())

        return incident_info

    def _vary_severity(self, base_severity: str, variation: int) -> str:
        """Vary severity for synthetic incidents."""
        severities = ["low", "medium", "high"]
        base_index = severities.index(base_severity)

        # Create some variation
        if variation % 10 == 0:
            return severities[(base_index + 1) % 3]  # Occasionally change severity
        else:
            return base_severity

    def run_ingestion(self) -> dict[str, int]:
        """Run complete Wave 3 history ingestion."""
        logger.info("Starting Wave 3: History ingestion...")

        results = {}

        # Ingest git history and incidents
        results["git_history"] = self.ingest_git_history()
        results["incident_rca"] = self.ingest_incident_rca()
        results["synthetic_incidents"] = self.ingest_synthetic_incidents()

        # Log statistics
        logger.info("Wave 3 history ingestion complete:")
        for category, count in results.items():
            logger.info(f"  {category}: {count} items")

        # Post-ingest stats are best-effort. ChromaDB's background compactor
        # can race with an immediate count() and raise InternalError; that
        # does not invalidate the ingested data. Log the skip rather than
        # failing the whole run.
        for coll in ("repo_git_history", "repo_incidents_rca"):
            try:
                stats = self.chroma.get_collection_stats(coll)
                logger.info(f"Collection '{coll}': {stats['document_count']} total documents")
            except (chromadb.errors.InternalError, RuntimeError) as exc:
                logger.warning(f"Could not read stats for '{coll}' post-ingest: {exc}")

        return results


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Wave 3: History Ingestion")
    parser.add_argument("--repo-root", default=".", help="Repository root directory")
    parser.add_argument("--chroma-dir", default=canonical_persist_dir_str(), help="ChromaDB persistence directory")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be ingested without actually doing it"
    )
    args = parser.parse_args()

    # Run ingestion
    ingestion = HistoryIngestion(
        repo_root=args.repo_root,
        chroma_persist_dir=args.chroma_dir,
    )

    if args.dry_run:
        logger.info("DRY RUN: Would ingest history data into ChromaDB")
        return

    results = ingestion.run_ingestion()

    # Summary
    total_items = sum(results.values())
    logger.info(f"Wave 3 complete: {total_items} total history items ingested")


if __name__ == "__main__":
    main()
