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

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, OPS_SCRIPTS_DIR
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "gravity_validator")
emit_determinism_digest("p0", "gravity_validator")

_emit_dispatches_healing_run("p1", "gravity_validator", "L5")
_emit_routes_through("p1", "gravity_validator", "L5")
_emit_escalates_to_human("p1", "gravity_validator", "L5")
_emit_reads_policy_state("p1", "gravity_validator", "L5")

_emit_applies_guardrail("p0", "gravity_validator", "p0_governance")
_emit_snapshots_state("p0", "gravity_validator", "state_snapshot")

CHECK_ID = "gravity_violations"
_LAYER_DIR_PATTERN = re.compile("^L[0-6]_")


def _get_apps_roots() -> frozenset[str]:
    """Derive apps_* roots from PROJECT_ROOT_WHITELIST — zero hardcoded folder names."""
    from agentic_core.L5_safety.config.structure_blueprint import PROJECT_ROOT_WHITELIST

    return frozenset(k for k in PROJECT_ROOT_WHITELIST if k.startswith("apps_"))


_APPS_ROOTS: frozenset[str] = _get_apps_roots()
_EXCLUDED_PATHS: tuple[str, ...] = (OPS_SCRIPTS_DIR, "scripts")
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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "GravityValidatorAgent.scan")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:GravityValidatorAgent.scan".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        try:
            from agentic_core.L5_safety.reasoning.StructuralValidatorAgent import (
                StructuralValidatorAgent,
                StructureConfig,
            )
        except ImportError as exc:
            logger.error("[GravityValidatorAgent] StructuralValidatorAgent import failed: %s", exc)
            return []
        config = StructureConfig(project_root=self.project_root, excluded_paths=_EXCLUDED_PATHS)
        enforcer = StructuralValidatorAgent(config=config)
        results = enforcer.validate_structure(self.project_root)
        root_str = str(self.project_root).replace("\\", "/")

        def _in_sovereign_scope(v: object) -> bool:
            fp = str(getattr(v, "file_path", v.get("file_path", "") if isinstance(v, dict) else "")).replace(
                "\\", "/"
            )
            # guardian: allow-path-string
            rel = fp.replace(root_str + "/", "", 1)
            parts = [p for p in rel.split("/") if p]
            if not parts:
                return False
            root = parts[0]
            if root in _APPS_ROOTS:
                return True
            if root == AGENTIC_CORE_DIR and len(parts) > 1:
                return bool(_LAYER_DIR_PATTERN.match(parts[1]))
            return False

        def _not_excluded(v: object) -> bool:
            fp = str(getattr(v, "file_path", v.get("file_path", "") if isinstance(v, dict) else "")).replace(
                "\\", "/"
            )
            return not any(ex in fp for ex in _EXCLUDED_PATHS)

        def _has_known_layers(v: object) -> bool:
            """Exclude violations where both layers are unknown — unactionable noise."""
            src = getattr(v, "source_layer", "?") or "?"
            tgt = getattr(v, "target_layer", "?") or "?"
            return not (src == "?" and tgt == "?")

        import ast as _ast

        _ast_cache: dict[str, _ast.Module] = {}

        def _parse_cached(fp_str: str) -> _ast.Module | None:
            if fp_str in _ast_cache:
                return _ast_cache[fp_str]
            try:
                from pathlib import Path as _Path

                tree = _ast.parse(_Path(fp_str).read_text(encoding="utf-8", errors="replace"))
                _ast_cache[fp_str] = tree
                return tree
            except Exception:
                _ast_cache[fp_str] = None
                return None

        def _is_module_level_import(v: object) -> bool:
            """Return True only if the violation's import is at module scope (not inside a function/class)."""
            fp = str(getattr(v, "file_path", v.get("file_path", "") if isinstance(v, dict) else ""))
            ln = int(getattr(v, "line_number", 0) or 0)
            if not fp or not ln:
                return True
            tree = _parse_cached(fp)
            if tree is None:
                return True
            for node in tree.body:
                if isinstance(node, (_ast.Import, _ast.ImportFrom)) and node.lineno == ln:
                    return True
            return False

        return [
            v
            for v in results.violations
            if _not_excluded(v)
            and _in_sovereign_scope(v)
            and _has_known_layers(v)
            and _is_module_level_import(v)
        ]

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
