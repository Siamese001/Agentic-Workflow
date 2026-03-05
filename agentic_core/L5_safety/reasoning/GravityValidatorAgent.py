"""
GravityValidatorAgent - L5 Pure Validator.

Detects layer gravity violations (upward imports, layer inversions) via
StructuralValidatorAgent without mutating the codebase. Emits a structured
check dict consumed by heal_gravity_violations via HEALER_REGISTRY.

This is the detection-half counterpart to GravityLeakRepairAgent (healer).
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

CHECK_ID = "gravity_violations"

_LAYER_DIR_PATTERN = re.compile(r"^L[0-6]_")
_APPS_ROOTS: frozenset[str] = frozenset({"apps_lic", "apps_rg", "apps_shared"})
_EXCLUDED_PATHS: tuple[str, ...] = ("ops_scripts", "scripts")

logger = logging.getLogger(__name__)


class GravityValidatorAgent:
    """L5 Certify-only validator for layer gravity violations."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def scan(self) -> list[Any]:
        """Run StructuralValidatorAgent and return filtered gravity violations.

        Returns:
            List of violation objects in the sovereign scope.
        """
        try:
            from agentic_core.L5_safety.reasoning.StructuralValidatorAgent import (
                StructuralValidatorAgent,
                StructureConfig,
            )
        except ImportError as exc:
            logger.error("[GravityValidatorAgent] StructuralValidatorAgent import failed: %s", exc)
            return []

        config = StructureConfig(
            project_root=self.project_root,
            excluded_paths=_EXCLUDED_PATHS,
        )
        enforcer = StructuralValidatorAgent(config=config)
        results = enforcer.validate_structure(self.project_root)

        root_str = str(self.project_root).replace("\\", "/")

        def _in_sovereign_scope(v: object) -> bool:
            fp = str(getattr(v, "file_path", v.get("file_path", "") if isinstance(v, dict) else "")).replace(
                "\\", "/"
            )
            rel = fp.replace(root_str + "/", "", 1)  # guardian: allow-path-fragility
            parts = [p for p in rel.split("/") if p]
            if not parts:
                return False
            root = parts[0]
            if root in _APPS_ROOTS:
                return True
            if root == "agentic_core" and len(parts) > 1:
                return bool(_LAYER_DIR_PATTERN.match(parts[1]))
            return False

        def _not_excluded(v: object) -> bool:
            fp = str(getattr(v, "file_path", v.get("file_path", "") if isinstance(v, dict) else "")).replace(
                "\\", "/"
            )
            return not any(ex in fp for ex in _EXCLUDED_PATHS)

        return [v for v in results.violations if _not_excluded(v) and _in_sovereign_scope(v)]

    def to_check_dict(self) -> dict[str, Any]:
        """Return structured check dict for _invoke_healer dispatch."""
        violations = self.scan()
        return {
            "check_id": CHECK_ID,
            "evidence": {"violations": violations},
            "violations_count": len(violations),
            "repo_root": str(self.project_root),
        }

    def run(self) -> dict[str, Any]:
        """Alias for to_check_dict for orchestrator compatibility."""
        return self.to_check_dict()
