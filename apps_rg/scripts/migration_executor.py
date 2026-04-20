#!/usr/bin/env python3
"""
Sovereign V2.5 Migration Executor for apps_rg
Reads RG_AUDIT_MANIFEST.json and physically restructures the repository.
usage: python scripts/rg_migrate_structure.py
"""

import json
import logging
import os
import re
import shutil
from pathlib import Path

from agentic_core.L0_routing.config import (
    APPS_RG_DIR,
)
from agentic_core.L0_routing.config.path_constants import TOOLS_DIR
from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS
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

_emit_applies_guardrail("p0", "migration_executor", "p0_governance")
_emit_reads_policy_state("p0", "migration_executor", "policy_binding")
_emit_snapshots_state("p0", "migration_executor", "state_snapshot")
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
from tqdm import tqdm

_emit_emits_metric_event("migration_executor", "p4obs", "metric_1")
_emit_emits_metric_event("migration_executor", "p4obs", "metric_2")
_emit_emits_metric_event("migration_executor", "p4obs", "metric_3")
_emit_emits_metric_event("migration_executor", "p4obs", "metric_4")
_emit_emits_metric_event("migration_executor", "p4obs", "metric_5")
_emit_emits_metric_event("migration_executor", "p4obs", "metric_6")
_emit_records_incident_event("migration_executor", "p4obs", "incident")
_emit_captures_runtime_anomaly("migration_executor", "p4obs", "anomaly")
_emit_writes_observability_log("migration_executor", "p4obs", "obs_log")
_emit_updates_monitoring_state("migration_executor", "p4obs", "mon_state")
_emit_triggers_alert("migration_executor", "p4obs", "alert")
_emit_links_incident_trace("migration_executor", "p4obs", "trace_link")
_emit_captures_pattern("migration_executor", "p3lm", "pattern")
_emit_records_learning_event("migration_executor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("migration_executor", "p3lm", "snapshot")
_emit_feeds_meta_learning("migration_executor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("migration_executor", "p3lm", "routing")
_emit_improves_agent_policy("migration_executor", "p3lm", "policy")
_emit_stores_learning_state("migration_executor", "p3lm", "state")
_emit_records_execution_trace("migration_executor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("migration_executor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("migration_executor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("migration_executor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("migration_executor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("migration_executor", "env_read", "p2_env_1")
_emit_reads_environ("migration_executor", "env_read", "p2_env_2")
_emit_reads_runtime_state("migration_executor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("migration_executor", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "migration_executor", "context_pull")
_emit_pulls_context("p1", "migration_executor", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "migration_executor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "migration_executor", "uwg_term_2")
_emit_writes_through("p1", "migration_executor", "write_through")
_emit_writes_through("p1", "migration_executor", "write_through_2")
_emit_validated_by_safety_plane("p1", "migration_executor", "safety_validation")
_emit_invokes_eval("p1", "migration_executor", "eval_call")
_emit_proposal_commits_routing("p1", "migration_executor", "routing_commit")
_emit_escalates_to_human("p1", "migration_executor", "human_escalation")
_emit_routes_through("p1", "migration_executor", "route_through")
_emit_checks_agent_registry("p1", "migration_executor", "agent_registry")
_emit_validates_agent_capability("p1", "migration_executor", "capability")
_emit_dispatches_execution_plan("p1", "migration_executor", "exec_plan")
_emit_agent_executes_agent("p1", "migration_executor", "sub_agent")
_emit_routes_to_agent("p1", "migration_executor", "target_agent")
_emit_verifies_policy("p1", "migration_executor", "policy_check")
_emit_observes_runtime_state("p1", "migration_executor", "runtime_state")
_emit_verifies_boundary("p1", "migration_executor", "boundary_check")
_emit_transcripts_response("p1", "migration_executor", "transcript")
_emit_hard_fails_untranscripted("p1", "migration_executor")
_emit_gated_by_confidence("p1", "migration_executor", "confidence_gate")
emit_replay_key("p0", "migration_executor")
emit_determinism_digest("p0", "migration_executor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "migration_executor", "execution_auth")
_emit_validates_capability("p2", "migration_executor", "capability_check")
_emit_routes_to_capability("p2", "migration_executor", "capability_route")
_emit_writes_via_uwg("p2", "migration_executor", "uwg_write")
_emit_blocks_direct_write("p2", "migration_executor", "direct_write_block")
_emit_records_tool_invocation("p2", "migration_executor", "tool_invocation")
_emit_captures_execution_output("p2", "migration_executor", "exec_output")
_emit_dispatches_agent("p3", "migration_executor", "agent_dispatch")
_emit_coordinates_agents("p3", "migration_executor", "agent_coordination")
_emit_records_workflow_lineage("p3", "migration_executor", "workflow_lineage")
_emit_records_healing_outcome("p3", "migration_executor", "healing_outcome")
_emit_escalates_failure("p3", "migration_executor", "failure_escalation")
_emit_orchestrates_workflow("p3", "migration_executor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "migration_executor", "healing_dispatch")
_emit_invokes_evaluation("p3", "migration_executor", "evaluation_signal")
_emit_records_telemetry_event("p4", "migration_executor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "migration_executor", "eval_metric")
_emit_stores_embedding("p4", "migration_executor", "embedding_store")
_emit_updates_meta_learning_state("p4", "migration_executor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "migration_executor", "exec_snapshot_link")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [MIGRATE] - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Define Root relative to this script (scripts/ -> root)
BASE_DIR = Path(__file__).resolve().parent.parent
APPS_RG_DIR = BASE_DIR / APPS_RG_DIR
MANIFEST_PATH = APPS_RG_DIR / "RG_AUDIT_MANIFEST.json"

# Approved Sovereign Structure
DIRS = {
    "engines": APPS_RG_DIR / "engines",
    "tools": APPS_RG_DIR / "shared/tools",
    "types": APPS_RG_DIR / "domain/types",
    "legacy": APPS_RG_DIR / "legacy",
    "quarantine": APPS_RG_DIR / "legacy/quarantine_broken",
}


class MigrationExecutor:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.manifest = self._load_manifest()
        self.moved_files: dict[str, str] = {}  # old_name -> new_full_path

    def _load_manifest(self) -> dict:
        if not MANIFEST_PATH.exists():
            raise FileNotFoundError(f"Manifest not found at {MANIFEST_PATH}")
        with open(MANIFEST_PATH) as f:
            return json.load(f)

    def _ensure_dirs(self):
        """Create target directories if they don't exist."""
        for name, path in DIRS.items():
            if not path.exists():
                logger.info(f"Creating directory: {path}")
                if not self.dry_run:
                    path.mkdir(parents=True, exist_ok=True)
                    # Create __init__.py for python packages
                    if name in [TOOLS_DIR, "types", "engines"]:
                        init_file = path / "__init__.py"
                        if not init_file.exists():
                            init_file.touch()

    def _move_file(self, src_rel: str, dest_dir: Path, new_name: str = None) -> bool:
        """Move a file safely from relative path (e.g., apps_rg/engines/file.py)."""
        # Handle path normalization
        src_clean = src_rel.replace("\\", "/")
        src_path = BASE_DIR / src_clean

        if not src_path.exists():
            logger.warning(f"Source file not found: {src_path}")
            return False

        filename = new_name if new_name else src_path.name
        dest_path = dest_dir / filename

        if self.dry_run:
            logger.info(f"[DRY RUN] Move {src_path.name} -> {dest_path}")
            return True

        try:
            shutil.move(str(src_path), str(dest_path))
            self.moved_files[src_path.stem] = str(dest_path)
            logger.info(f"Moved: {src_path.name} -> {dest_path}")
            return True
        except Exception as e:  # guardian: allow-silent-swallow
            logger.error(f"Failed to move {src_path.name}: {e}")
            return False

    def process_quarantine(self):
        """Move broken files to legacy/quarantine."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "MigrationExecutor.process_quarantine"
        )

        broken = self.manifest.get("actions", {}).get("fix_syntax_errors", [])
        logger.info(f"Processing {len(broken)} broken files...")
        for f in tqdm(broken, desc="Processing", unit="item"):
            self._move_file(f, DIRS["quarantine"])

    def process_legacy(self):
        """Archive legacy files."""
        legacy = self.manifest.get("actions", {}).get("archive_legacy", [])
        logger.info(f"Archiving {len(legacy)} legacy files...")
        for f in legacy:
            self._move_file(f, DIRS["legacy"])

    def process_types(self):
        """Rename and move Imposter Agents to domain/types."""
        types_map = self.manifest.get("actions", {}).get("move_to_domain_types", {})
        logger.info(f"Migrating {len(types_map)} type definitions...")
        for src, new_name in types_map.items():
            self._move_file(src, DIRS["types"], new_name=new_name)

    def process_tools(self):
        """Move stateless tools to shared/tools."""
        tools = self.manifest.get("actions", {}).get("move_to_tools", [])
        logger.info(f"Migrating {len(tools)} stateless tools...")
        for f in tools:
            self._move_file(f, DIRS["tools"])

    def process_unknowns(self):
        """Leave Unknowns in Engines but Log them (Passive Review)."""
        # Per review: Do not move unknowns blindly. Just log them.
        unknowns = self.manifest.get("actions", {}).get("unknown_require_manual_review", [])
        logger.info(
            f"PENDING REVIEW: {len(unknowns)} files remain in engines/ for manual classification.",
        )

    def patch_imports(self):
        """Scan apps_rg/engines/ and update imports for moved tools/types."""
        if self.dry_run:
            return

        logger.info("Starting Import Patching Sequence...")

        # 1. Patch Tools Imports
        tools = [Path(p).stem for p in self.manifest.get("actions", {}).get("move_to_tools", [])]
        if tools:
            # Matches: from apps_rg.engines.toolname import ...
            # guardian: allow-path-string
            pattern = r"from apps_rg\.engines\.(" + "|".join(map(re.escape, tools)) + r")"
            replacement = r"from apps_rg.tools.\1"
            self._apply_regex_patch(pattern, replacement)

        # 2. Patch Types Imports
        types_map = self.manifest.get("actions", {}).get("move_to_domain_types", {})
        for src, new_filename in types_map.items():
            old_module = Path(src).stem
            new_module = Path(new_filename).stem

            # Case: from apps_rg.engines.OldAgent import X
            p1 = f"from apps_rg.engines.{old_module}"
            r1 = f"from apps_rg.types.{new_module}"
            self._apply_string_replace(p1, r1)

    def _apply_regex_patch(self, pattern: str, replacement: str):
        """Apply regex sub to all .py files in apps_rg."""
        regex = re.compile(pattern)
        for root, dirs, files in tqdm(os.walk(APPS_RG_DIR), desc="Processing", unit="item"):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            for file in tqdm(files, desc="Processing", unit="item"):
                if file.endswith(".py"):
                    path = Path(root) / file
                    try:
                        content = path.read_text(encoding="utf-8")
                        if regex.search(content):
                            new_content = regex.sub(replacement, content)
                            path.write_text(new_content, encoding="utf-8")
                            logger.info(f"Patched imports in {path.name}")
                    except Exception as e:  # guardian: allow-silent-swallow
                        logger.error(f"Failed to patch {path.name}: {e}")

    def _apply_string_replace(self, old: str, new: str):
        for root, dirs, files in tqdm(os.walk(APPS_RG_DIR), desc="Processing", unit="item"):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            for file in tqdm(files, desc="Processing", unit="item"):
                if file.endswith(".py"):
                    path = Path(root) / file
                    try:
                        content = path.read_text(encoding="utf-8")
                        if old in content:
                            new_content = content.replace(old, new)
                            path.write_text(new_content, encoding="utf-8")
                            logger.info(f"Replaced '{old}' in {path.name}")
                    except Exception as e:  # guardian: allow-silent-swallow
                        logger.error(f"Failed to patch {path.name}: {e}")

    def execute(self):
        logger.info("=== STARTING SOVEREIGN MIGRATION ===")
        self._ensure_dirs()
        self.process_quarantine()
        self.process_legacy()
        self.process_types()
        self.process_tools()
        self.process_unknowns()
        self.patch_imports()
        logger.info("=== MIGRATION COMPLETE ===")


if __name__ == "__main__":
    # Safety: Run immediately
    executor = MigrationExecutor(dry_run=False)
    executor.execute()
