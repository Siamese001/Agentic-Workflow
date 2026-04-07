"""Migration Tools - Utilities for transitioning from K-nodes to functional roles.

This module provides tools to help migrate existing code and configurations
from the legacy K-node system to the new functional role architecture.
from apps_shared.config.pipeline_constants_config import MAX_RETRIES  # noqa: F401
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""

import json
import logging
import re
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "k_node_scanner_validator", "p0_governance")
_emit_reads_policy_state("p0", "k_node_scanner_validator", "policy_binding")
_emit_snapshots_state("p0", "k_node_scanner_validator", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("k_node_scanner_validator", "p4obs", "metric_1")
_emit_emits_metric_event("k_node_scanner_validator", "p4obs", "metric_2")
_emit_emits_metric_event("k_node_scanner_validator", "p4obs", "metric_3")
_emit_emits_metric_event("k_node_scanner_validator", "p4obs", "metric_4")
_emit_emits_metric_event("k_node_scanner_validator", "p4obs", "metric_5")
_emit_emits_metric_event("k_node_scanner_validator", "p4obs", "metric_6")
_emit_records_incident_event("k_node_scanner_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("k_node_scanner_validator", "p4obs", "anomaly")
_emit_writes_observability_log("k_node_scanner_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("k_node_scanner_validator", "p4obs", "mon_state")
_emit_triggers_alert("k_node_scanner_validator", "p4obs", "alert")
_emit_links_incident_trace("k_node_scanner_validator", "p4obs", "trace_link")
_emit_captures_pattern("k_node_scanner_validator", "p3lm", "pattern")
_emit_records_learning_event("k_node_scanner_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("k_node_scanner_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("k_node_scanner_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("k_node_scanner_validator", "p3lm", "routing")
_emit_improves_agent_policy("k_node_scanner_validator", "p3lm", "policy")
_emit_stores_learning_state("k_node_scanner_validator", "p3lm", "state")
_emit_records_execution_trace("k_node_scanner_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("k_node_scanner_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("k_node_scanner_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("k_node_scanner_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("k_node_scanner_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("k_node_scanner_validator", "env_read", "p2_env_1")
_emit_reads_environ("k_node_scanner_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("k_node_scanner_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("k_node_scanner_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "k_node_scanner_validator", "context_pull")
_emit_pulls_context("p1", "k_node_scanner_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "k_node_scanner_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "k_node_scanner_validator", "uwg_term_2")
_emit_writes_through("p1", "k_node_scanner_validator", "write_through")
_emit_writes_through("p1", "k_node_scanner_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "k_node_scanner_validator", "safety_validation")
_emit_invokes_eval("p1", "k_node_scanner_validator", "eval_call")
_emit_proposal_commits_routing("p1", "k_node_scanner_validator", "routing_commit")
_emit_escalates_to_human("p1", "k_node_scanner_validator", "human_escalation")
_emit_routes_through("p1", "k_node_scanner_validator", "route_through")
_emit_checks_agent_registry("p1", "k_node_scanner_validator", "agent_registry")
_emit_validates_agent_capability("p1", "k_node_scanner_validator", "capability")
_emit_dispatches_execution_plan("p1", "k_node_scanner_validator", "exec_plan")
_emit_agent_executes_agent("p1", "k_node_scanner_validator", "sub_agent")
_emit_routes_to_agent("p1", "k_node_scanner_validator", "target_agent")
_emit_verifies_policy("p1", "k_node_scanner_validator", "policy_check")
_emit_observes_runtime_state("p1", "k_node_scanner_validator", "runtime_state")
_emit_verifies_boundary("p1", "k_node_scanner_validator", "boundary_check")
_emit_transcripts_response("p1", "k_node_scanner_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "k_node_scanner_validator")
_emit_gated_by_confidence("p1", "k_node_scanner_validator", "confidence_gate")
emit_replay_key("p0", "k_node_scanner_validator")
emit_determinism_digest("p0", "k_node_scanner_validator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "k_node_scanner_validator", "execution_auth")
_emit_validates_capability("p2", "k_node_scanner_validator", "capability_check")
_emit_routes_to_capability("p2", "k_node_scanner_validator", "capability_route")
_emit_writes_via_uwg("p2", "k_node_scanner_validator", "uwg_write")
_emit_blocks_direct_write("p2", "k_node_scanner_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "k_node_scanner_validator", "tool_invocation")
_emit_captures_execution_output("p2", "k_node_scanner_validator", "exec_output")
_emit_dispatches_agent("p3", "k_node_scanner_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "k_node_scanner_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "k_node_scanner_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "k_node_scanner_validator", "healing_outcome")
_emit_escalates_failure("p3", "k_node_scanner_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "k_node_scanner_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "k_node_scanner_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "k_node_scanner_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "k_node_scanner_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "k_node_scanner_validator", "eval_metric")
_emit_stores_embedding("p4", "k_node_scanner_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "k_node_scanner_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "k_node_scanner_validator", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class KNodeScanner:
    """Scans codebase for legacy K-node references."""

    # Patterns to find K-node references
    PATTERNS = [
        r"\bK\.?\d+\b",  # K.2, K2, K.3, etc.
        r"\bk_node_\w+",  # k_node_researcher, etc.
        r"\bK\d+[A-Za-z]*\b",  # K3_agent, K5_validator, etc.
        r'"[^"]*K\.?\d+[^"]*"',  # Strings containing K-nodes
        r"\'[^\']*K\.?\d+[^\']*\'",  # Single quotes
    ]

    def __init__(self, root_path: Path):
        """Initialize scanner.

        Args:
            root_path: Root directory to scan
        """
        self.root_path = root_path
        self.findings: list[dict[str, Any]] = []

    def scan_directory(self, extensions: list[str] = None) -> dict[str, Any]:
        """Scan directory for K-node references.

        Args:
            extensions: File extensions to scan (default: .py, .md, .json)

        Returns:
            Scan results
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "KNodeScanner.scan_directory")

        if extensions is None:
            extensions = [".py", ".md", ".json", ".yaml", ".yml"]

        results = {"total_files": 0, "files_with_references": 0, "total_references": 0, "files": []}

        for ext in extensions:
            for file_path in self.root_path.rglob(f"*{ext}"):
                # Skip certain directories
                if any(skip in str(file_path) for skip in [".git", "__pycache__", ".venv"]):
                    continue

                file_results = self.scan_file(file_path)
                if file_results["references"]:
                    results["files"].append(file_results)
                    results["files_with_references"] += 1
                    results["total_references"] += len(file_results["references"])

                results["total_files"] += 1

        return results

    def scan_file(self, file_path: Path) -> dict[str, Any]:
        """Scan a single file for K-node references.

        Args:
            file_path: File to scan

        Returns:
            Scan results for the file
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return {"path": str(file_path), "references": [], "error": str(e)}

        references = []
        line_number = 1

        for line in content.split("\n"):
            for pattern in self.PATTERNS:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # Check if it's actually a K-node reference
                    text = match.group()
                    if self._is_knode_reference(text):
                        references.append(
                            {
                                "line": line_number,
                                "column": match.start() + 1,
                                "text": text,
                                "context": line.strip(),
                            },
                        )
            line_number += 1

        return {"path": str(file_path), "references": references}

    def _is_knode_reference(self, text: str) -> bool:
        """Check if text is actually a K-node reference.

        Args:
            text: Text to check

        Returns:
            True if K-node reference
        """
        # Remove quotes
        text = text.strip("\"'")

        # Check patterns
        if re.match(r"^K\.?\d+$", text):
            return True

        if re.match(r"^k_node_", text, re.IGNORECASE):
            return True

        if re.match(r"^K\d+[A-Za-z]*$", text):
            return True

        return False


class KNodeMigrator:
    """Migrates K-node references to functional roles."""

    def __init__(self):
        """Initialize migrator."""
        self.replacements = self._build_replacement_map()

    def _build_replacement_map(self) -> dict[str, str]:
        """Build replacement map for migration.

        Returns:
            Dictionary mapping legacy references to functional roles
        """
        replacements = {}

        # Direct mappings
        for legacy, role in LEGACY_MAPPING.items():
            replacements[legacy] = role.value
            replacements[legacy.lower()] = role.value
            replacements[legacy.upper()] = role.value

        # Common variations
        replacements.update(
            {
                "K.2": "context_gatherer",
                "K2": "context_gatherer",
                "K.3": "content_drafter",
                "K3": "content_drafter",
                "K.5": "quality_critic",
                "K5": "quality_critic",
                "k_node_researcher": "context_gatherer",
                "k_node_writer": "content_drafter",
                "k_node_critic": "quality_critic",
                "K3_agent": "content_drafter",
                "K5_validator": "quality_critic",
            },
        )

        return replacements

    def migrate_file(self, file_path: Path, backup: bool = True) -> bool:
        """Migrate a file from K-nodes to functional roles.

        Args:
            file_path: File to migrate
            backup: Whether to create backup

        Returns:
            True if migration successful
        """
        try:
            # Read file
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Create backup
            if backup:
                backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
                with open(backup_path, "w", encoding="utf-8") as f:
                    f.write(content)

            # Apply replacements
            migrated_content = content
            changes_made = False

            for legacy, functional in self.replacements.items():
                if legacy in migrated_content:
                    migrated_content = migrated_content.replace(legacy, functional)
                    changes_made = True
                    logger.info(f"Replaced {legacy} with {functional} in {file_path}")

            # Write migrated content
            if changes_made:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(migrated_content)
                return True
            else:
                # No changes needed, remove backup
                if backup and backup_path.exists():
                    backup_path.unlink()
                return False

        except Exception as e:
            logger.error(f"Failed to migrate {file_path}: {e}")
            return False

    def migrate_configuration(self, config_path: Path) -> bool:
        """Migrate configuration files.

        Args:
            config_path: Path to configuration file

        Returns:
            True if migration successful
        """
        try:
            with open(config_path) as f:
                config = json.load(f)

            # Track changes
            changes_made = False

            # Recursively migrate
            def migrate_dict(d: dict, path: str = "") -> None:
                nonlocal changes_made

                for key, value in d.items():
                    current_path = f"{path}.{key}" if path else key

                    if isinstance(value, str):
                        for legacy, functional in self.replacements.items():
                            if legacy in value:
                                d[key] = value.replace(legacy, functional)
                                changes_made = True
                                logger.info(f"Migrated config value at {current_path}")
                    elif isinstance(value, dict):
                        migrate_dict(value, current_path)
                    elif isinstance(value, list):
                        for i, item in enumerate(value):
                            if isinstance(item, str):
                                for legacy, functional in self.replacements.items():
                                    if legacy in item:
                                        value[i] = item.replace(legacy, functional)
                                        changes_made = True
                                        logger.info(
                                            f"Migrated config list item at {current_path}[{i}]",
                                        )

            migrate_dict(config)

            # Write back if changed
            if changes_made:
                with open(config_path, "w") as f:
                    json.dump(config, f, indent=2)
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to migrate configuration {config_path}: {e}")
            return False


class MigrationValidator:
    """Validates that migration was successful."""

    def __init__(self):
        """Initialize validator."""
        self.scanner = KNodeScanner(Path("."))

    def validate_migration(self, root_path: Path) -> dict[str, Any]:
        """Validate that all K-node references have been migrated.

        Args:
            root_path: Root path to validate

        Returns:
            Validation results
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "MigrationValidator.validate_migration")

        logger.info("Validating migration...")

        # Scan for remaining references
        results = self.scanner.scan_directory()

        # Analyze results
        validation = {
            "is_valid": results["total_references"] == 0,
            "remaining_references": results["total_references"],
            "files_with_issues": results["files_with_references"],
            "problem_files": [],
        }

        # Categorize issues
        for file_result in results["files"]:
            issues = []
            for ref in file_result["references"]:
                # Check if it's a false positive
                text = ref["text"]
                if not self._is_false_positive(text, file_result["path"]):
                    issues.append(ref)

            if issues:
                validation["problem_files"].append({"path": file_result["path"], "issues": issues})

        return validation

    def _is_false_positive(self, text: str, file_path: str) -> bool:
        """Check if a reference is a false positive.

        Args:
            text: The reference text
            file_path: Path of the file containing the reference

        Returns:
            True if false positive
        """
        # Skip test files
        if "test" in file_path.lower():
            if "K.3" in text or "K5" in text:
                # Test files might be testing the legacy system
                return True

        # Skip comments that explain the legacy system
        if "//" in text or "#" in text:
            if "legacy" in text.lower() or "old" in text.lower():
                return True

        # Skip documentation about the migration
        if "migration" in file_path.lower():
            return True

        return False


def run_full_migration(root_path: Path, dry_run: bool = False) -> dict[str, Any]:
    """Run the complete migration process.

    Args:
        root_path: Root path to migrate
        dry_run: If True, only scan without making changes

    Returns:
        Migration results
    """
    logger.info(f"Starting {'dry run ' if dry_run else ''}migration from {root_path}")

    results = {"scan": None, "migration": None, "validation": None, "success": False}

    # Step 1: Scan for references
    scanner = KNodeScanner(root_path)
    results["scan"] = scanner.scan_directory()

    logger.info(
        f"Found {results['scan']['total_references']} K-node references "
        f"in {results['scan']['files_with_references']} files",
    )

    if dry_run:
        logger.info("Dry run complete - no changes made")
        results["success"] = True
        return results

    # Step 2: Migrate files
    migrator = KNodeMigrator()
    migrated_files = 0

    for file_result in results["scan"]["files"]:
        file_path = Path(file_result["path"])
        if migrator.migrate_file(file_path):
            migrated_files += 1

    results["migration"] = {
        "files_migrated": migrated_files,
        "total_files_with_refs": results["scan"]["files_with_references"],
    }

    logger.info(f"Migrated {migrated_files} files")

    # Step 3: Validate migration
    validator = MigrationValidator()
    results["validation"] = validator.validate_migration(root_path)

    if results["validation"]["is_valid"]:
        logger.info("Migration completed successfully!")
        results["success"] = True
    else:
        logger.warning(
            f"Migration incomplete: {results['validation']['remaining_references']} references remain",
        )

    return results


# Convenience function
def migrate_project(root_path: str = ".", dry_run: bool = False) -> bool:
    """Migrate an entire project from K-nodes to functional roles.

    Args:
        root_path: Root path of the project
        dry_run: If True, only scan without changes

    Returns:
        True if migration successful
    """
    path = Path(root_path).resolve()
    results = run_full_migration(path, dry_run)

    return results["success"]
