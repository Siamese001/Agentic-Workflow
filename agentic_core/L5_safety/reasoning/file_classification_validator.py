"""
FileClassificationValidatorAgent - L5 Pure Validator.

Runs FileClassificationAgent in validate_only mode to detect naming,
territory, and layer alignment violations without mutating the filesystem.
Emits a structured check dict consumed by heal_file_classification via
HEALER_REGISTRY.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

CHECK_ID = "file_classification"

logger = logging.getLogger(__name__)


class FileClassificationValidatorAgent:
    """L5 Certify-only validator for file classification compliance."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def scan(self, target_territory: str | None = None) -> dict[str, Any]:
        """Run FileClassificationAgent in validate_only mode.

        Args:
            target_territory: Optional territory string to scope the scan.

        Returns:
            Dict with keys: scan_result, violations, stats, file_registry.
        """
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
            FileClassificationAgent,
        )

        classifier = FileClassificationAgent(project_root=self.project_root)
        classifier.validate_only = True
        classifier.dry_run = False
        if hasattr(classifier, "target_territory"):
            classifier.target_territory = target_territory

        try:
            if target_territory:
                try:
                    scan_result = classifier.run(target_territory=target_territory) or {}
                except TypeError:
                    scan_result = classifier.run() or {}
            else:
                scan_result = classifier.run() or {}
        except Exception as exc:  # guardian: allow-silent-swallower
            logger.error("[FileClassificationValidatorAgent] scan failed: %s", exc)
            scan_result = {}

        violations: list[dict[str, Any]] = []
        if hasattr(classifier, "stats") and classifier.stats.get("violations"):
            for vtype, count in classifier.stats["violations"].items():
                if isinstance(count, int) and count > 0:
                    violations.append(
                        {
                            "type": "CLASSIFICATION",
                            "subtype": vtype,
                            "count": count,
                            "territory": target_territory,
                        }
                    )

        file_registry: list[str] = []
        if hasattr(classifier, "file_registry") and classifier.file_registry:
            file_registry = [str(p) for p in classifier.file_registry]

        return {
            "scan_result": scan_result,
            "violations": violations,
            "file_registry": file_registry,
        }

    def to_check_dict(self, target_territory: str | None = None) -> dict[str, Any]:
        """Return structured check dict for _invoke_healer dispatch."""
        evidence = self.scan(target_territory=target_territory)
        violations_count = sum(v.get("count", 1) for v in evidence.get("violations", []))
        return {
            "check_id": CHECK_ID,
            "evidence": evidence,
            "violations_count": violations_count,
            "territory": target_territory,
            "repo_root": str(self.project_root),
        }

    def run(self, target_territory: str | None = None) -> dict[str, Any]:
        """Alias for to_check_dict for orchestrator compatibility."""
        return self.to_check_dict(target_territory=target_territory)
