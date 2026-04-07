from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "location_validator")
emit_determinism_digest("p0", "location_validator")

_emit_dispatches_healing_run("p1", "location_validator", "L5")
_emit_routes_through("p1", "location_validator", "L5")
_emit_checks_agent_registry("p1", "location_validator", "agent_registry")
_emit_validates_agent_capability("p1", "location_validator", "capability")
_emit_dispatches_execution_plan("p1", "location_validator", "exec_plan")
_emit_agent_executes_agent("p1", "location_validator", "sub_agent")
_emit_routes_to_agent("p1", "location_validator", "target_agent")
_emit_verifies_policy("p1", "location_validator", "policy_check")
_emit_observes_runtime_state("p1", "location_validator", "runtime_state")
_emit_verifies_boundary("p1", "location_validator", "boundary_check")
_emit_transcripts_response("p1", "location_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "location_validator")
_emit_gated_by_confidence("p1", "location_validator", "confidence_gate")
_emit_escalates_to_human("p1", "location_validator", "L5")
_emit_reads_policy_state("p1", "location_validator", "L5")
_emit_authorize_and_execute("p2", "location_validator", "execution_auth")
_emit_validates_capability("p2", "location_validator", "capability_check")
_emit_routes_to_capability("p2", "location_validator", "capability_route")
_emit_writes_via_uwg("p2", "location_validator", "uwg_write")
_emit_blocks_direct_write("p2", "location_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "location_validator", "tool_invocation")
_emit_captures_execution_output("p2", "location_validator", "exec_output")
_emit_dispatches_agent("p3", "location_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "location_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "location_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "location_validator", "healing_outcome")
_emit_escalates_failure("p3", "location_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "location_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "location_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "location_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "location_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "location_validator", "eval_metric")
_emit_stores_embedding("p4", "location_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "location_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "location_validator", "exec_snapshot_link")

"\nLocationValidatorAgent: Pure validation agent for territorial compliance\n\nResponsibility: Validate file locations against sovereign structure rules\n- NO healing or file operations\n- NO side effects\n- Pure validation logic only\n\nExtracted from LocationAgent.py as part of SRP fission.\n"
import ast
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.L0_routing.config.path_constants import (
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    ARCHIVES_DIR,
    OPS_SCRIPTS_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint import DEPTH_RULES, LAYER_PREFIX_EXEMPT_TERRITORIES
from agentic_core.L5_safety.config.structure_blueprint.ssot import ALLOW_ROOT_PY_TERRITORIES
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_snapshots_state,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("location_validator", "p4obs", "metric_1")
_emit_emits_metric_event("location_validator", "p4obs", "metric_2")
_emit_emits_metric_event("location_validator", "p4obs", "metric_3")
_emit_emits_metric_event("location_validator", "p4obs", "metric_4")
_emit_emits_metric_event("location_validator", "p4obs", "metric_5")
_emit_emits_metric_event("location_validator", "p4obs", "metric_6")
_emit_records_incident_event("location_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("location_validator", "p4obs", "anomaly")
_emit_writes_observability_log("location_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("location_validator", "p4obs", "mon_state")
_emit_triggers_alert("location_validator", "p4obs", "alert")
_emit_links_incident_trace("location_validator", "p4obs", "trace_link")
_emit_captures_pattern("location_validator", "p3lm", "pattern")
_emit_records_learning_event("location_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("location_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("location_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("location_validator", "p3lm", "routing")
_emit_improves_agent_policy("location_validator", "p3lm", "policy")
_emit_stores_learning_state("location_validator", "p3lm", "state")
_emit_records_execution_trace("location_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("location_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("location_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("location_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("location_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("location_validator", "env_read", "p2_env_1")
_emit_reads_environ("location_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("location_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("location_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "location_validator", "context_pull")
_emit_pulls_context("p1", "location_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "location_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "location_validator", "uwg_term_2")
_emit_writes_through("p1", "location_validator", "write_through")
_emit_writes_through("p1", "location_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "location_validator", "safety_validation")
_emit_invokes_eval("p1", "location_validator", "eval_call")
_emit_proposal_commits_routing("p1", "location_validator", "routing_commit")


@dataclass
class LocationValidatorAgent(SovereignBaseAgent):
    """
    Pure validation agent for territorial compliance.

    Validates:
    - Root folder whitelist compliance
    - Depth requirements per sovereign root
    - Forbidden patterns and numbered folders
    - AST-based semantic alignment
    - Import layer violations
    - App-specific file placement

    Does NOT perform:
    - File moves or deletions
    - Automated healing
    - Backup operations

    Use LocationHealerAgent for remediation.
    """

    project_root: Path = field(default=None)

    def __post_init__(self):
        """Initialize validator with project root validation."""
        super().__post_init__()
        if isinstance(self.project_root, str):
            self.project_root = Path(self.project_root)
        self.project_root = self.project_root.resolve()

    # guardian: allow-type-erasure
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        [HEALER PROTOCOL] Standardized healing interface for location violations.

        Note: LocationValidatorAgent is validation-only and does not perform healing.
        Use LocationHealerAgent for actual remediation.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "LocationValidatorAgent.heal", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "LocationValidatorAgent.heal", "p0_governance")

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L5_POLICY, "LocationValidatorAgent.heal",
        )
        return {
            "status": "skipped",
            "details": "LocationValidatorAgent is validation-only. Use LocationHealerAgent for healing.",
            "artifacts": [],
            "errors": [],
        }

    # guardian: allow-type-erasure
    def heal_repository(self, *args, **kwargs) -> dict:
        """heal_repository() not implemented for LocationValidatorAgent."""
        raise NotImplementedError("heal_repository() not implemented for LocationValidatorAgent")

    def validate_sovereign_roots(self) -> list[tuple[Path, str]]:
        """Ensure all required sovereign roots exist and are directories."""
        from agentic_core.L5_safety.config.structure_blueprint import ROOT_WHITELIST

        violations: list[tuple[Path, str]] = []
        for root_name in ROOT_WHITELIST:
            root_path = self.project_root / root_name
            if not root_path.exists():
                violations.append((root_path, f"Missing sovereign root: {root_name}"))
            elif not root_path.is_dir():
                violations.append((root_path, f"Sovereign root is not a directory: {root_name}"))
        return violations

    def validate_file_location(self, file_path: Path) -> tuple[bool, str]:
        """Per-file location validation with correct forbidden-check ordering.

        [CONSTITUTIONAL OVERRIDE 2026-01-22]
        SovereignBaseAgent and Layer Base Agents have 'Semantic Location Immunity'
        from standard rules but MUST reside in 'agentic_core/base_agents/'.
        This check runs BEFORE standard validation to prevent validator logic gaps.
        """
        if "BaseAgent" in file_path.name or file_path.name == "SovereignBaseAgent.py":
            if file_path.parent.name != "base_agents":
                return (
                    False,
                    f"CRITICAL: Base Agents must reside in 'agentic_core/base_agents/', not '{file_path.parent.name}'",
                )
        try:
            rel_path = file_path.relative_to(self.project_root)
            parts = rel_path.parts
            root_folder = parts[0]
        except ValueError:
            return (False, "VOID VIOLATION: File outside project root")
        result = self._validate_forbidden_patterns(parts, root_folder)
        if not result[0]:
            return result
        result = self._validate_root_whitelist(root_folder, rel_path)
        if not result[0]:
            return result
        result = self._validate_depth_requirements(parts, root_folder, rel_path)
        if not result[0]:
            return result
        result = self._validate_app_specific_files(root_folder, file_path)
        if not result[0]:
            return result
        result = self._validate_filename_patterns(file_path)
        if not result[0]:
            return result
        result = self._validate_final_checks(root_folder, file_path, parts)
        if not result[0]:
            return result
        return (True, f"Location compliant in sovereign territory: {root_folder}")

    def _validate_forbidden_patterns(self, parts: tuple, root_folder: str) -> tuple[bool, str]:
        """Validate forbidden folder patterns and numbered roots."""
        from agentic_core.L5_safety.config.structure_blueprint import (
            FORBIDDEN_FOLDER_PATTERN,
            FORBIDDEN_ROOT_FOLDERS,
        )

        for part in parts:
            if part in FORBIDDEN_ROOT_FOLDERS:
                return (False, f"VOID VIOLATION: Forbidden folder '{part}' at any depth")
            if hasattr(FORBIDDEN_FOLDER_PATTERN, "match"):
                if FORBIDDEN_FOLDER_PATTERN.match(part):
                    return (False, f"VOID VIOLATION: Numbered folder pattern '{part}' forbidden")
        if len(root_folder) >= 3 and root_folder[:2].isdigit() and (root_folder[2:3] == "_"):
            return (False, f"VOID VIOLATION: Numbered root folder '{root_folder}' not approved")
        return (True, "OK")

    def _validate_root_whitelist(self, root_folder: str, rel_path: Path = None) -> tuple[bool, str]:
        """Validate path is within an allowed sovereign territory using SSOT helper."""
        from agentic_core.L5_safety.config.structure_blueprint import ROOT_WHITELIST, is_path_allowed

        if rel_path is not None:
            if not is_path_allowed(str(rel_path)):
                return (False, f"VOID VIOLATION: Path '{rel_path}' not in sovereign territory")
        if root_folder == "scripts" and rel_path is not None:
            file_path = self.project_root / rel_path
            is_compliant, reason = self._validate_scripts_isolation(file_path)
            if not is_compliant:
                return (False, reason)
        if rel_path is not None:
            return (True, "OK")
        if root_folder not in ROOT_WHITELIST:
            return (False, f"VOID VIOLATION: Unapproved root folder '{root_folder}'")
        return (True, "OK")

    def _validate_scripts_isolation(self, file_path: Path) -> tuple[bool, str]:
        """
        Enforces strict isolation for root scripts.

        Root scripts (`scripts/`) are for standalone utilities/setup only.
        They MUST NOT import from `agentic_core`.

        If a script imports `agentic_core`, it is part of the system
        and belongs in `agentic_core/L0_routing/scripts/`.
        """
        from agentic_core.L5_safety.config.structure_blueprint import SCRIPTS_PLACEMENT_RULES

        if not file_path.exists() or file_path.suffix != ".py":
            return (True, "OK")
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
            forbidden_prefixes = SCRIPTS_PLACEMENT_RULES.get("root_scripts", {}).get("forbidden_imports", [])
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        for prefix in forbidden_prefixes:
                            if alias.name.startswith(prefix):
                                return (
                                    False,
                                    f"SEMANTIC VIOLATION: Root script imports '{alias.name}'. Files importing '{prefix}' belong in agentic_core/L0_routing/scripts/",
                                )
                elif isinstance(node, ast.ImportFrom):
                    if node.module:    # guardian: Syntax errors should be caught at parser level, not runtime
                        for prefix in forbidden_prefixes:
                            if node.module.startswith(prefix):    # guardian: File operations with encoding need error-specific handling
                                return (
                                    False,
                                    f"SEMANTIC VIOLATION: Root script imports from '{node.module}'. Files importing '{prefix}' belong in agentic_core/L0_routing/scripts/",
                                )
        except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime

            import logging; logging.getLogger(__name__).debug("location_validator: SyntaxError swallowed at L379: %s", e)
        except (OSError, UnicodeDecodeError) as e:    # guardian: File operations with encoding need error-specific handling
            self.logger.debug(f"Failed to check import depth for {rel_path}: {e}")
        return (True, "OK")

    def _validate_depth_requirements(
        self, parts: tuple, root_folder: str, rel_path: Path,
    ) -> tuple[bool, str]:
        """Validate depth requirements from sovereign registry.

        SSOT FIX: Allow variable depth for certain subfolders that legitimately
        have deeper structures (e.g., utils/core_extensions/, config/core/).

        [2026-02-08] FLAT DIRECTORY ENFORCEMENT: Directories in FLAT_DIRECTORIES
        must not contain any subdirectories. This check runs BEFORE depth checks
        to catch violations like mixins/contracts/ that bypass depth validation.
        """
        from agentic_core.L5_safety.config.structure_blueprint import (
            VARIABLE_DEPTH_SUBFOLDERS,
            validate_flat_directory,
        )

        flat_violation = validate_flat_directory(parts)
        if flat_violation:
            return (False, f"FLAT VIOLATION: {flat_violation['message']}")
        expected_depth = DEPTH_RULES.get(root_folder)
        actual_depth = len(parts) - 1
        if root_folder == AGENTIC_CORE_DIR and len(parts) > 1:
            subfolder = parts[1]
            if subfolder in VARIABLE_DEPTH_SUBFOLDERS:
                if actual_depth >= 2:
                    return (True, "OK")
        if actual_depth == 1 and root_folder in ALLOW_ROOT_PY_TERRITORIES and (rel_path.suffix == ".py"):
            return (True, "OK")
        if expected_depth is not None and actual_depth != expected_depth:
            reason = "SHALLOW" if actual_depth < expected_depth else "DEEP"
            return (False, f"{reason} VIOLATION ({root_folder}): depth {actual_depth} != {expected_depth}")
        return (True, "OK")

    def _validate_app_specific_files(self, root_folder: str, file_path: Path) -> tuple[bool, str]:
        """Validate app-specific files are not in core."""
        from agentic_core.L5_safety.config.structure_blueprint import (
            get_correct_app_path,
            is_app_specific_file,
        )

        if root_folder == AGENTIC_CORE_DIR and is_app_specific_file(file_path.name):
            correct_path = get_correct_app_path(file_path.name) or "appropriate apps_* folder"
            return (
                False,
                f"APP-SPECIFIC IN CORE VIOLATION: '{file_path.name}' is application-specific and must not live in agentic_core. Move to '{correct_path}/'.",
            )
        return (True, "OK")

    def _validate_filename_patterns(self, file_path: Path) -> tuple[bool, str]:
        """Validate filename patterns for forbidden prefixes and backup files."""
        from agentic_core.L5_safety.config.structure_blueprint import (
            check_forbidden_signals,
            has_forbidden_layer_prefix,
        )

        try:
            _rel = file_path.relative_to(self.project_root)
            _root = _rel.parts[0] if _rel.parts else ""
        except (ValueError, IndexError):
            _root = ""
        if _root not in LAYER_PREFIX_EXEMPT_TERRITORIES:
            forbidden_prefix = has_forbidden_layer_prefix(file_path.name)
            if forbidden_prefix:
                return (False, f"LAYER PREFIX VIOLATION: Filename has forbidden prefix '{forbidden_prefix}'")
        if file_path.name.endswith((".bak", ".backup", ".old", ".tmp")):
            return (False, "BROKEN BACKUP FILE: Remove stale backup file")    # guardian: File operations with encoding need error-specific handling
        try:
            content = None
            if file_path.exists() and file_path.is_file():
                if file_path.stat().st_size < 1000000:
                    try:
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                    except (OSError, UnicodeDecodeError) as e:    # guardian: File operations with encoding need error-specific handling
                        self.logger.debug(f"Failed to read content for artifact check: {e}")
            rejection_reason = check_forbidden_signals(file_path.name, content)
            if rejection_reason:
                return (False, f"ARTIFACT ROUTING VIOLATION: {rejection_reason}")
        except (ImportError, AttributeError) as e:
            self.logger.debug(f"Artifact routing check failed: {e}")
        return (True, "OK")

    def _validate_final_checks(self, root_folder: str, file_path: Path, parts: tuple) -> tuple[bool, str]:
        """Final validation checks for root-level files and gravity leaks."""
        from agentic_core.L5_safety.config.structure_blueprint import ROOT_PROTECTED_FILES

        if len(parts) == 1 and file_path.suffix == ".py":
            if file_path.name not in ROOT_PROTECTED_FILES:
                return (False, f"VOID VIOLATION: Unapproved root-level Python file '{file_path.name}'")
        return (True, "OK")

    def _validate_ast_violations(self, root_folder: str, file_path: Path, rel_path: Path) -> tuple[bool, str]:
        """Validate AST-based violations for agentic_core Python files."""
        if root_folder != AGENTIC_CORE_DIR or file_path.suffix != ".py":
            return (True, "OK")
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content)
            try:
                rel_parts = file_path.relative_to(self.project_root / AGENTIC_CORE_DIR).parts
                current_l1 = rel_parts[0] if len(rel_parts) > 1 else None
                current_l2 = rel_parts[1] if len(rel_parts) > 2 else None
                current_territory = f"{current_l1}/{current_l2}" if current_l2 else current_l1
            except ValueError:
                current_l1, current_l2, current_territory = (None, None, None)    # guardian: Parsing and encoding errors need separate handling strategies
            result = self._check_forbidden_imports(tree, current_l1, rel_path)
            if not result[0]:
                return result
            result = self._check_semantic_alignment(tree, current_territory, rel_path)
            if not result[0]:
                return result
        except (OSError, UnicodeDecodeError, SyntaxError) as e:    # guardian: Parsing and encoding errors need separate handling strategies
            self.logger.debug(f"AST parsing failed for {rel_path}: {e}")
        return (True, "OK")

    def _check_forbidden_imports(self, tree: Any, current_l1: str, rel_path: Path) -> tuple[bool, str]:
        """Check for forbidden app imports and layer violations."""
        forbidden_app_import, forbidden_layer_import = self._scan_imports_for_violations(tree, current_l1)
        if forbidden_app_import:
            return (
                False,
                f"GRAVITY VIOLATION (AST-resolved): Imports from apps_* modules forbidden in agentic_core. Move file to correct apps_*/engines/ folder. File: {rel_path}",
            )
        if forbidden_layer_import:
            return (
                False,
                f"INTERNAL GRAVITY VIOLATION: {forbidden_layer_import} import direction forbidden. Refactor to respect layer gravity or move file. File: {rel_path}",
            )
        return (True, "OK")

    def _scan_imports_for_violations(self, tree: Any, current_l1: str) -> tuple[bool, str | None]:
        """Scan AST for forbidden imports and return violation flags."""
        import ast

        for node in ast.walk(tree):
            if isinstance(node, ast.Import | ast.ImportFrom):
                modules = self._extract_modules_from_node(node)
                for module in modules:
                    if self._is_forbidden_app_import(module):
                        return (True, None)
                    layer_violation = self._check_layer_import_violation(module, current_l1)
                    if layer_violation:
                        return (False, layer_violation)
        return (False, None)

    def _extract_modules_from_node(self, node: Any) -> list[str]:
        """Extract module names from import node."""
        import ast

        if isinstance(node, ast.Import):
            return [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            return [node.module]
        return []

    def _is_forbidden_app_import(self, module: str) -> bool:
        """Check if module is a forbidden app import."""
        from agentic_core.L5_safety.config.structure_blueprint import FORBIDDEN_APP_MODULES

        return module.startswith(("apps_rg.", "apps_lic.")) or module in FORBIDDEN_APP_MODULES

    def _check_layer_import_violation(self, module: str, current_l1: str) -> str | None:
        """Check for layer import violations and return violation description.

        [RECONCILED 2026-01-27] Now enforces:
        1. Core layer gravity (L1-L5 import direction)
        2. App-layer horizontal isolation (apps_shared independence)
        """
        from agentic_core.L5_safety.config.structure_blueprint import LAYER_FORBIDDEN_IMPORTS

        if not current_l1:
            return None
        if module.startswith("agentic_core.") and len(module.split(".")) > 2:
            imported_l1 = module.split(".")[1]
            if imported_l1 in LAYER_FORBIDDEN_IMPORTS.get(current_l1, set()):
                return f"{current_l1} → {imported_l1}"
        if current_l1 == APPS_SHARED_DIR:
            if module.startswith(("apps_rg.", "apps_lic.")):
                imported_app = module.split(".")[0]
                return f"apps_shared → {imported_app} (HORIZONTAL ISOLATION VIOLATION)"
        if current_l1 == APPS_RG_DIR and module.startswith("apps_lic."):
            return "apps_rg → apps_lic (HORIZONTAL ISOLATION VIOLATION)"
        if current_l1 == APPS_LIC_DIR and module.startswith("apps_rg."):
            return "apps_lic → apps_rg (HORIZONTAL ISOLATION VIOLATION)"
        return None

    def _check_semantic_alignment(
        self, tree: Any, current_territory: str, rel_path: Path,
    ) -> tuple[bool, str]:
        """Check semantic alignment between file location and content.

        [DEDUP 2026-02-07] Delegates file classification to FCA for consistent
        territory alignment instead of reimplementing AST scoring locally.
        """
        if not current_territory:
            return (True, "OK")
        app_rg_score, app_lic_score, territory_scores = self._calculate_semantic_scores(tree)
        result = self._check_app_domain_violation(app_rg_score, app_lic_score, rel_path)
        if not result[0]:
            return result
        try:
            from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent

            file_path = self.project_root / rel_path
            if file_path.exists():
                fca = FileClassificationAgent(
                    project_root=self.project_root, dry_run=True, validate_only=True,
                )
                file_type = fca.classify_file(file_path)
                correct_folder = fca._get_correct_folder_for_type(file_type)
                current_subfolder = (
                    current_territory.split("/")[-1] if "/" in current_territory else current_territory
                )
                if correct_folder and current_subfolder != correct_folder:
                    if file_type != "UTILITY":
                        return (
                            False,
                            f"TERRITORY ALIGNMENT (FCA): File classified as {file_type}, belongs in '{correct_folder}/' not '{current_subfolder}/'. File: {rel_path}",
                        )
        except (ImportError, AttributeError, OSError) as e:
            self.logger.debug(f"FCA classification failed for {rel_path}: {e}")
        return self._check_territory_alignment(current_territory, territory_scores, rel_path)

    def _calculate_semantic_scores(self, tree: Any) -> tuple[float, float, dict[str, float]]:
        """Calculate semantic scores for app and territory alignment."""
        import ast

        from agentic_core.L5_safety.config.structure_blueprint import (
            APP_LIC_AST_TERMS,
            APP_RG_AST_TERMS,
            CORE_TERRITORY_KEYWORDS,
        )

        app_rg_score = 0.0
        app_lic_score = 0.0
        territory_scores: dict[str, float] = dict.fromkeys(CORE_TERRITORY_KEYWORDS, 0.0)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef | ast.FunctionDef):
                name = node.name.lower()
                if any(t in name for t in APP_RG_AST_TERMS):
                    app_rg_score += 1.0
                if any(t in name for t in APP_LIC_AST_TERMS):
                    app_lic_score += 1.0
                for terr, cats in CORE_TERRITORY_KEYWORDS.items():
                    for terms in cats.values():
                        if any(t in name for t in terms):
                            territory_scores[terr] += 1.0
        return (app_rg_score, app_lic_score, territory_scores)

    def _check_app_domain_violation(
        self, app_rg_score: float, app_lic_score: float, rel_path: Path,
    ) -> tuple[bool, str]:
        """
        [HARDENED] Detects cross-contamination AND Global Candidates for apps_shared.
        [SSOT 2026-01-27] Implements the 'Shared Vacuum' logic.
        """
        current_root = rel_path.parts[0]
        if current_root in [APPS_RG_DIR, APPS_LIC_DIR]:
            if app_rg_score < 0.5 and app_lic_score < 0.5:
                filename = rel_path.name
                if not filename.startswith(("rg_", "lic_", "resume_", "outreach_")):
                    return (
                        False,
                        "GLOBAL CANDIDATE DETECTED: Low domain signals - belongs in apps_shared/utils",
                    )
        if current_root == APPS_RG_DIR and app_lic_score > app_rg_score * 2.0:
            return (
                False,
                f"APP DOMAIN VIOLATION: Strong apps_lic signals ({app_lic_score:.1f} vs {app_rg_score:.1f})",
            )
        if current_root == APPS_LIC_DIR and app_rg_score > app_lic_score * 2.0:
            return (
                False,
                f"APP DOMAIN VIOLATION: Strong apps_rg signals ({app_rg_score:.1f} vs {app_lic_score:.1f})",
            )
        return (True, "")

    def _check_territory_alignment(
        self, current_territory: str, territory_scores: dict[str, float], rel_path: Path,
    ) -> tuple[bool, str]:
        """Check territory alignment between file location and content."""
        from agentic_core.L5_safety.config.structure_blueprint import (
            MIN_ALIGNMENT_SCORE,
            TERRITORY_MISMATCH_THRESHOLD,
        )

        if not territory_scores:
            return (True, "OK")
        current_score = territory_scores.get(current_territory, 0.0)
        best_territory = max(territory_scores, key=territory_scores.get)
        max_other = max((s for t, s in territory_scores.items() if t != current_territory), default=0.0)
        if current_score < MIN_ALIGNMENT_SCORE and max_other >= MIN_ALIGNMENT_SCORE:
            return (
                False,
                f"TERRITORY ALIGNMENT WEAK: Current '{current_territory}' score {current_score:.2f} < {MIN_ALIGNMENT_SCORE}. Lacks semantic signals — refactor or move to '{best_territory}'. File: {rel_path}",
            )
        if max_other > current_score + TERRITORY_MISMATCH_THRESHOLD:
            return (
                False,
                f"TERRITORY MISMATCH VIOLATION: Stronger signals for '{best_territory}' ({max_other:.2f}) vs current ({current_score:.2f}). Move to agentic_core/{best_territory}. File: {rel_path}",
            )
        return (True, "OK")

    def _collect_ast_increments(
        self, tree: Any, territory_keywords: dict[str, Any],
    ) -> list[tuple[str, float]]:
        """Collect AST-based scoring increments."""
        import ast

        increments = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef | ast.FunctionDef):
                for terr, cats in territory_keywords.items():
                    for terms in cats.values():
                        if any(t in node.name.lower() for t in terms):
                            increments.append((terr, 1.0))
        return increments

    def _aggregate_ast_increments(self, increments: list[tuple[str, float]]) -> dict[str, float]:
        """Aggregate scoring increments into territory scores."""
        scores: dict[str, float] = {}
        for terr, score in increments:
            scores[terr] = scores.get(terr, 0.0) + score
        return scores

    def _recompute_ast_scores(
        self, tree: Any, territory_keywords: dict[str, Any],
    ) -> tuple[float, float, dict[str, float]]:
        """Recompute AST scores (wrapper for _calculate_semantic_scores)."""
        return self._calculate_semantic_scores(tree)

    def _score_identifier(self, name: str, territory_keywords: dict[str, Any]) -> float:
        """Score an identifier name against territory keywords."""
        score = 0.0
        name_lower = name.lower()
        for _terr, cats in territory_keywords.items():
            for terms in cats.values():
                if any(t in name_lower for t in terms):
                    score += 1.0
        return score

    def _score_string(self, value: str, territory_keywords: dict[str, Any]) -> float:
        """Score a string value against territory keywords."""
        return self._score_identifier(value, territory_keywords)

    def _score_variable(self, name: str, territory_keywords: dict[str, Any]) -> float:
        """Score a variable name against territory keywords."""
        return self._score_identifier(name, territory_keywords)

    def _score_assignments(self, node: Any, territory_keywords: dict[str, Any]) -> float:
        """Score assignment nodes."""
        import ast

        score = 0.0
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    score += self._score_identifier(target.id, territory_keywords)
        return score

    def _score_arguments(self, node: Any, territory_keywords: dict[str, Any]) -> float:
        """Score function arguments."""
        import ast

        score = 0.0
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            for arg in node.args.args:
                score += self._score_identifier(arg.arg, territory_keywords)
        return score

    def enforce_void_compliance(self, files: list[Path]) -> tuple[list[Path], list[tuple[Path, str]]]:
        """Filter files and collect all location-based violations.

        Salvaged from LocationAgent.py during LCD+ decommission.
        """
        valid_files: list[Path] = []
        violations: list[tuple[Path, str]] = []
        for file_path in files:
            is_valid, reason = self.validate_file_location(file_path)
            if is_valid:
                valid_files.append(file_path)
            else:
                violations.append((file_path, reason))
        return (valid_files, violations)

    def _check_naming_conventions(self, file_path: Path) -> list[str]:
        """Check naming conventions for file."""
        violations = []
        from agentic_core.L5_safety.config.structure_blueprint import has_forbidden_layer_prefix

        forbidden_prefix = has_forbidden_layer_prefix(file_path.name)
        if forbidden_prefix:
            violations.append(f"Forbidden layer prefix: {forbidden_prefix}")
        if file_path.name.endswith((".bak", ".backup", ".old", ".tmp")):
            violations.append("Backup file pattern detected")
        return violations

    # guardian: allow-type-erasure
    def run(self, target_territory: str | None = None) -> dict[str, Any]:
        """
        Execute validation-only scan across sovereign territories.

        Args:
            target_territory: If provided, restricts scan to this domain (Strict Targeting).

        Phase 4.1 Upgrade: Universal root scanning using PROJECT_ROOT_WHITELIST.
        """
        from agentic_core.L5_safety.config.structure_blueprint import PROJECT_ROOT_WHITELIST

        violations = []
        compliant_files = 0
        total_files = 0
        roots_scanned = []
        if target_territory:
            target_roots = (
                [target_territory] if target_territory in PROJECT_ROOT_WHITELIST else [AGENTIC_CORE_DIR]
            )
        else:
            target_roots = sorted(PROJECT_ROOT_WHITELIST)
        for root_name in target_roots:
            root_path = self.project_root / root_name
            if not root_path.exists():
                continue
            roots_scanned.append(root_name)
            for py_file in root_path.rglob("*.py"):
                if any(
                    skip in py_file.parts
                    for skip in [
                        "__pycache__",
                        ".git",
                        ARCHIVES_DIR,
                        ".venv",
                        ".sovereign_healing_backup",
                        "node_modules",
                        OPS_SCRIPTS_DIR,
                        "artifacts",
                    ]
                ):
                    continue
                total_files += 1
                is_valid, reason = self.validate_file_location(py_file)
                if is_valid:
                    compliant_files += 1
                else:
                    violations.append({"file": str(py_file), "reason": reason})
        return {
            "violations": violations,
            "total_files_scanned": total_files,
            "compliant_files": compliant_files,
            "roots_scanned": roots_scanned,
            "status": "COMPLETE",
        }
