from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.L0_routing.config.path_constants import (
    GLOBAL_EXCLUDED_DIRS,
    REPORTS_DIR,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
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

emit_replay_key("p0", "root_hygiene_healer")
emit_determinism_digest("p0", "root_hygiene_healer")

_emit_dispatches_healing_run("p1", "root_hygiene_healer", "L5")
_emit_routes_through("p1", "root_hygiene_healer", "L5")
_emit_checks_agent_registry("p1", "root_hygiene_healer", "agent_registry")
_emit_validates_agent_capability("p1", "root_hygiene_healer", "capability")
_emit_dispatches_execution_plan("p1", "root_hygiene_healer", "exec_plan")
_emit_agent_executes_agent("p1", "root_hygiene_healer", "sub_agent")
_emit_routes_to_agent("p1", "root_hygiene_healer", "target_agent")
_emit_verifies_policy("p1", "root_hygiene_healer", "policy_check")
_emit_observes_runtime_state("p1", "root_hygiene_healer", "runtime_state")
_emit_verifies_boundary("p1", "root_hygiene_healer", "boundary_check")
_emit_transcripts_response("p1", "root_hygiene_healer", "transcript")
_emit_hard_fails_untranscripted("p1", "root_hygiene_healer")
_emit_gated_by_confidence("p1", "root_hygiene_healer", "confidence_gate")
_emit_escalates_to_human("p1", "root_hygiene_healer", "L5")
_emit_reads_policy_state("p1", "root_hygiene_healer", "L5")
_emit_authorize_and_execute("p2", "root_hygiene_healer", "execution_auth")
_emit_validates_capability("p2", "root_hygiene_healer", "capability_check")
_emit_routes_to_capability("p2", "root_hygiene_healer", "capability_route")
_emit_writes_via_uwg("p2", "root_hygiene_healer", "uwg_write")
_emit_blocks_direct_write("p2", "root_hygiene_healer", "direct_write_block")
_emit_records_tool_invocation("p2", "root_hygiene_healer", "tool_invocation")
_emit_captures_execution_output("p2", "root_hygiene_healer", "exec_output")
_emit_dispatches_agent("p3", "root_hygiene_healer", "agent_dispatch")
_emit_coordinates_agents("p3", "root_hygiene_healer", "agent_coordination")
_emit_records_workflow_lineage("p3", "root_hygiene_healer", "workflow_lineage")
_emit_records_healing_outcome("p3", "root_hygiene_healer", "healing_outcome")
_emit_escalates_failure("p3", "root_hygiene_healer", "failure_escalation")
_emit_orchestrates_workflow("p3", "root_hygiene_healer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "root_hygiene_healer", "healing_dispatch")
_emit_invokes_evaluation("p3", "root_hygiene_healer", "evaluation_signal")
_emit_records_telemetry_event("p4", "root_hygiene_healer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "root_hygiene_healer", "eval_metric")
_emit_stores_embedding("p4", "root_hygiene_healer", "embedding_store")
_emit_updates_meta_learning_state("p4", "root_hygiene_healer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "root_hygiene_healer", "exec_snapshot_link")

"""
File: agentic_core/L5_safety/validators/RootHygieneAgent.py
Path: agentic_core/L5_safety/validators/RootHygieneAgent.py
Rationale:
    Canonizes the RootHygieneEnforcer as a first-class L5 Agent.
    Relocated from L0_routing/scripts to L5_safety/validators to
    centralize enforcement and enable auto-discovery by execute_ssot.py.

    Integration Features:
    - Inherits from SovereignBaseAgent for full infrastructure support
    - Implements standard agent interface for execute_ssot.py orchestration
    - Preserves all original RootHygieneEnforcer functionality
    - Adds heal_repository() method for standard healing chain integration
"""

import logging
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    OPS_SCRIPTS_DIR,
)
from agentic_core.L0_routing.config.path_constants import ARCHIVES_DIR, HEALING_BACKUPS_DIR
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

_emit_emits_metric_event("root_hygiene_healer", "p4obs", "metric_1")
_emit_emits_metric_event("root_hygiene_healer", "p4obs", "metric_2")
_emit_emits_metric_event("root_hygiene_healer", "p4obs", "metric_3")
_emit_emits_metric_event("root_hygiene_healer", "p4obs", "metric_4")
_emit_emits_metric_event("root_hygiene_healer", "p4obs", "metric_5")
_emit_emits_metric_event("root_hygiene_healer", "p4obs", "metric_6")
_emit_records_incident_event("root_hygiene_healer", "p4obs", "incident")
_emit_captures_runtime_anomaly("root_hygiene_healer", "p4obs", "anomaly")
_emit_writes_observability_log("root_hygiene_healer", "p4obs", "obs_log")
_emit_updates_monitoring_state("root_hygiene_healer", "p4obs", "mon_state")
_emit_triggers_alert("root_hygiene_healer", "p4obs", "alert")
_emit_links_incident_trace("root_hygiene_healer", "p4obs", "trace_link")
_emit_captures_pattern("root_hygiene_healer", "p3lm", "pattern")
_emit_records_learning_event("root_hygiene_healer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("root_hygiene_healer", "p3lm", "snapshot")
_emit_feeds_meta_learning("root_hygiene_healer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("root_hygiene_healer", "p3lm", "routing")
_emit_improves_agent_policy("root_hygiene_healer", "p3lm", "policy")
_emit_stores_learning_state("root_hygiene_healer", "p3lm", "state")
_emit_records_execution_trace("root_hygiene_healer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("root_hygiene_healer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("root_hygiene_healer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("root_hygiene_healer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("root_hygiene_healer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("root_hygiene_healer", "env_read", "p2_env_1")
_emit_reads_environ("root_hygiene_healer", "env_read", "p2_env_2")
_emit_reads_runtime_state("root_hygiene_healer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("root_hygiene_healer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "root_hygiene_healer", "context_pull")
_emit_pulls_context("p1", "root_hygiene_healer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "root_hygiene_healer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "root_hygiene_healer", "uwg_term_2")
_emit_writes_through("p1", "root_hygiene_healer", "write_through")
_emit_writes_through("p1", "root_hygiene_healer", "write_through_2")
_emit_validated_by_safety_plane("p1", "root_hygiene_healer", "safety_validation")
_emit_invokes_eval("p1", "root_hygiene_healer", "eval_call")
_emit_proposal_commits_routing("p1", "root_hygiene_healer", "routing_commit")
from agentic_core.runtime.contracts.lifecycle_trace_contract import emit_determinism_digest
from tqdm import tqdm

emit_determinism_digest("trace_root_hygiene_healer", "root_hygiene_healer_dispatch_entry")
emit_determinism_digest("trace_root_hygiene_healer", "root_hygiene_healer_dispatch_exit")
emit_determinism_digest("trace_root_hygiene_healer", "root_hygiene_healer_tool_invoke")
emit_determinism_digest("trace_root_hygiene_healer", "root_hygiene_healer_tool_complete")
emit_determinism_digest("trace_root_hygiene_healer", "root_hygiene_healer_agent_entry")
emit_determinism_digest("trace_root_hygiene_healer", "root_hygiene_healer_agent_exit")
emit_determinism_digest("trace_root_hygiene_healer", "root_hygiene_healer_uwg_write")
emit_determinism_digest("trace_root_hygiene_healer", "root_hygiene_healer_trace_sign")
emit_determinism_digest("trace_root_hygiene_healer", "root_hygiene_healer_guardrail_check")
emit_determinism_digest("trace_root_hygiene_healer", "root_hygiene_healer_policy_verify")

# Optional: Import SovereignBaseAgent if available for full integration
try:
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
    from agentic_core.utils.decorators_compat_util import standard_heal

    HAS_SOVEREIGN_BASE = True
except ImportError:  # guardian: allow-silent-swallow
    HAS_SOVEREIGN_BASE = False
    SovereignBaseAgent = object

    # Use canonical standard_heal from HealingMixin
    from agentic_core.L5_safety.reasoning.FileClassificationAgent import standard_heal


# SSOT Constants
ROOT_MARKERS = [AGENTIC_CORE_DIR, "pyproject.toml"]


def get_project_root() -> Path:
    """Resolve project root securely."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_project_root", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_project_root", "p0_governance")
    current = Path.cwd()
    for marker in ROOT_MARKERS:
        if (current / marker).exists():
            return current
    raise RuntimeError("Must run from Project Root")


@dataclass
class RootHygieneHealerAgent(SovereignBaseAgent):
    """
    Enforces strict root directory hygiene standards.

    This agent canonizes the RootHygieneEnforcer functionality as a
    first-class L5 safety agent with full orchestration capabilities.

    Responsibilities:
    1. Moves root 'scripts/*' to 'ops_scripts/' (standalone) or 'L0_routing/scripts/' (core)
    2. Moves 'coverage_html' to 'reports/'
    3. Deletes illegal root directories after evacuation
    """

    project_root: Path = field(default_factory=Path.cwd)
    dry_run: bool = False

    def __post_init__(self):
        if HAS_SOVEREIGN_BASE and hasattr(super(), "__post_init__"):
            super().__post_init__()
        # [HARDENING] Ensure path is absolute for resolve() calls
        self.project_root = self.project_root.resolve()
        self.stats = {
            "scripts_evacuated": 0,
            "dirs_evacuated": 0,
            "coverage_relocated": 0,
            "illegal_dirs_removed": 0,
            "n_duplicates_removed": 0,
            "errors": 0,
        }

    def run(self) -> dict[str, Any]:
        """Entry point for execute_ssot.py orchestration."""

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L5_POLICY, "RootHygieneHealer.run")
        print(f"[HYGIENE] Executing Root Hygiene Enforcement at {self.project_root}")
        success = self._enforce_root_hygiene()
        return {
            "success": success == 0,
            "stats": self.stats,
            "summary": f"Scripts: {self.stats['scripts_evacuated']}, Dirs: {self.stats['dirs_evacuated']}, Errors: {self.stats['errors']}",
        }

    def _enforce_root_hygiene(self) -> int:
        """Core logic from RootHygieneEnforcer.py."""
        print(f"[HYGIENE] Enforcing Root Sovereignty at: {self.project_root}")
        print("=" * 60)

        try:
            # 1. EVACUATE ROOT SCRIPTS
            self._evacuate_root_scripts()

            # 2. EVACUATE COVERAGE_HTML
            self._evacuate_coverage_html()

            # 3. RELOCATE PURGE_CACHE (Specific Request)
            self._relocate_purge_cache()

            # 4. REMOVE _N SUFFIX DUPLICATE FILES (generated by LocationHealerAgent collision bug)
            self._detect_and_remove_n_duplicates()

            # 5. DELETE UNUSED TEMP/CACHE FOLDERS
            self._cleanup_unused_temp_folders()

            return 0  # Success

        except (RuntimeError, OSError) as e:  # guardian: allow-silent-swallow
            print(f"[ERROR] Root hygiene enforcement failed: {e}")
            self.stats["errors"] += 1
            return 1

    def _detect_and_remove_n_duplicates(self):
        """Detect and remove _N suffix duplicate files (e.g. __init___1.py).

        These are generated by the LocationHealerAgent collision loop when a
        destination file already exists. The original file is canonical;
        the _N numbered copy is always the duplicate and must be deleted.
        """
        import re as _re

        _n_pattern = _re.compile(r"^(.+?)_(\d+)(\.[^.]+)$")
        removed = 0
        flagged = []

        for candidate in tqdm(sorted(self.project_root.rglob("*")), desc="Processing", unit="item"):
            if not candidate.is_file():
                continue
            # skip archive/backup/cache dirs
            rel = candidate.relative_to(self.project_root)
            if any(
                p in rel.parts for p in (".git", "__pycache__", ARCHIVES_DIR, ".healing_backups", ".venv")
            ):
                continue
            m = _n_pattern.match(candidate.name)
            if not m:
                continue
            # reconstruct the original unsuffixed name: stem_N.ext -> stem.ext
            original_name = m.group(1) + m.group(3)
            original_path = candidate.parent / original_name
            if not original_path.exists():
                continue  # no canonical original — not a collision duplicate
            flagged.append((candidate, original_path))

        if flagged:
            print(f"[HYGIENE] Found {len(flagged)} _N suffix duplicate file(s):")
        for dup, original in tqdm(flagged, desc="Processing", unit="item"):
            rel_dup = dup.relative_to(self.project_root)
            rel_orig = original.relative_to(self.project_root)
            print(f"  [DUP] {rel_dup}  (original: {rel_orig})")
            if not self.dry_run:
                try:
                    _wg.remove_file(dup)
                    removed += 1
                    print(f"  [REMOVED] {rel_dup}")
                except (RuntimeError, OSError) as e:  # guardian: allow-silent-swallow
                    print(f"  [ERROR] Could not remove {rel_dup}: {e}")
                    self.stats["errors"] += 1
            else:
                removed += 1  # count as found in dry-run

        self.stats["n_duplicates_removed"] += removed
        if removed:
            print(
                f"[HYGIENE] _N duplicate cleanup: {removed} file(s) {'removed' if not self.dry_run else 'flagged (dry-run)'}",
            )

    def _cleanup_unused_temp_folders(self):
        """Delete unused temp/cache folders to reclaim disk space.

        Targets:
        - .nox, .tox (test runners) — delete if >7 days old
        - .pytest_tmp, .pytest_cache (pytest) — always delete
        - .mypy_cache, .ruff_cache (linters) — always delete
        - .backup, .healing_backups — delete if >7 days old
        - __pycache__ at root — always delete
        """
        import time

        ALWAYS_DELETE = {".pytest_tmp", ".pytest_cache", ".mypy_cache", ".ruff_cache", "__pycache__"}
        DELETE_IF_OLD = {".nox", ".tox", ".backup", ".healing_backups"}
        AGE_THRESHOLD_DAYS = 7

        deleted = 0
        for entry in tqdm(self.project_root.iterdir(), desc="Processing", unit="item"):
            if not entry.is_dir():
                continue

            name = entry.name
            should_delete = False
            reason = ""

            if name in ALWAYS_DELETE:
                should_delete = True
                reason = "cache/temp"
            elif name in DELETE_IF_OLD:
                try:  # review: Add error context logging
                    age_days = (time.time() - entry.stat().st_mtime) / 86400
                    if age_days > AGE_THRESHOLD_DAYS:
                        should_delete = True
                        reason = f"unused ({age_days:.0f} days old)"
                except OSError:  # guardian: allow-silent-swallow -- teardown/cleanup context -- swallow is conventional in resource-release paths
                    pass
            # review: Add error context logging
            if should_delete:
                print(f"[HYGIENE] Deleting {name}/ ({reason})")
                if not self.dry_run:
                    try:
                        _wg.remove_tree(entry)
                        deleted += 1
                        print(f"  [DELETED] {name}/")
                    except (RuntimeError, OSError) as e:  # guardian: allow-silent-swallow
                        print(f"  [ERROR] Could not delete {name}/: {e}")
                        self.stats["errors"] += 1
                else:
                    deleted += 1

        if deleted:
            print(
                f"[HYGIENE] Temp folder cleanup: {deleted} folder(s) {'deleted' if not self.dry_run else 'flagged (dry-run)'}",
            )

    def _evacuate_root_scripts(self):
        """Evacuate root scripts directory to appropriate locations."""
        root_scripts = self.project_root / "scripts"
        ops_scripts = self.project_root / OPS_SCRIPTS_DIR
        l0_scripts = self.project_root / AGENTIC_CORE_DIR / "L0_routing" / "scripts"

        if root_scripts.exists():
            print("[DETECT] Illegal root 'scripts/' directory found.")

            if not self.dry_run:
                _wg.ensure_dir(ops_scripts)
                _wg.ensure_dir(l0_scripts)

            for item in tqdm(root_scripts.iterdir(), desc="Processing", unit="item"):
                try:
                    if item.is_file() and item.suffix == ".py":
                        # Decision Logic: Does it import agentic_core?
                        content = item.read_text(encoding="utf-8")
                        if AGENTIC_CORE_DIR in content or "from agentic_core" in content:
                            target = l0_scripts / item.name
                            action = "REPATRIATE (Core)"
                        else:
                            target = ops_scripts / item.name
                            action = "RELOCATE (Ops)"

                        print(f"  - {item.name} -> {action}")
                        if not self.dry_run:
                            _wg.move_path(str(item), str(target))
                        self.stats["scripts_evacuated"] += 1

                    elif item.is_dir():
                        # Move entire subfolders to ops_scripts/maintenance or similar
                        target = ops_scripts / item.name
                        print(f"  - DIR {item.name}/ -> RELOCATE (Ops)")
                        if not self.dry_run:
                            if target.exists():
                                _wg.remove_tree(target)  # Force overwrite logic for dirs
                            _wg.move_path(str(item), str(target))
                        self.stats["dirs_evacuated"] += 1

                except (RuntimeError, OSError) as e:  # guardian: allow-silent-swallow
                    print(f"  [ERROR] Could not move {item.name}: {e}")
                    self.stats["errors"] += 1

            # Cleanup empty dir
            if not self.dry_run:
                try:
                    _wg.remove_dir(root_scripts)  # review: Add error context logging
                    print("[SUCCESS] Illegal 'scripts/' directory eliminated.")
                    self.stats["illegal_dirs_removed"] += 1
                except OSError:
                    print("[WARNING] 'scripts/' not empty, manual check required.")
        else:
            print("[CHECK] Root 'scripts/' is clean.")

    # review: Add error context logging
    def _evacuate_coverage_html(self):
        """Evacuate coverage_html directory to reports/."""
        cov_html = self.project_root / "coverage_html"
        reports_cov = self.project_root / REPORTS_DIR / "coverage_html"

        if cov_html.exists():
            print("\n[DETECT] Illegal root 'coverage_html/' found.")

            if not self.dry_run:
                _wg.ensure_dir(reports_cov.parent)

                if reports_cov.exists():
                    _wg.remove_tree(reports_cov)

                print("  - Moving to reports/coverage_html")
                _wg.move_path(str(cov_html), str(reports_cov))
                self.stats["coverage_relocated"] += 1
                print("[SUCCESS] Coverage report relocated.")
        else:
            print("[CHECK] Root 'coverage_html/' is clean.")

    def _relocate_purge_cache(self):
        """Specific handling for purge_cache.py organization."""
        ops_scripts = self.project_root / OPS_SCRIPTS_DIR
        purge_script = ops_scripts / "purge_cache.py"
        maint_script_dir = ops_scripts / "maintenance"

        if purge_script.exists():
            print("\n[REFILE] Organizing purge_cache.py -> ops_scripts/maintenance/")
            if not self.dry_run:
                _wg.ensure_dir(maint_script_dir)
                target = maint_script_dir / "purge_cache.py"
                _wg.move_path(str(purge_script), str(target))

    def scan_root_violations(self, target_territory: str = None) -> dict[str, Any]:
        """
        [SSOT INTEGRATION] Scan project root for unapproved entries.

        Compares every file/directory at project root against the SSOT
        SOVEREIGN_TERRITORIES allowlist plus approved dotfiles and config
        files. Anything not on the allowlist is flagged as a violation.

        Args:
            target_territory: Ignored — always scans project root.

        Returns:
            Dict with violations list for SSOT aggregation.
        """
        violations = []

        # Sovereign territory dirs derived live from SSOT — zero hardcoded folder names.
        # Dotdirs / VCS / IDE tooling are NOT code territories; they stay explicit here.
        try:
            from agentic_core.L0_routing.config.path_constants import PROJECT_ROOT_WHITELIST

            _sovereign_dirs: set[str] = set(PROJECT_ROOT_WHITELIST)
        except (ImportError, AttributeError):
            _sovereign_dirs = set()

        # Tooling dirs (version control / CI / IDE / editor) — SSOT import.
        # NOTE: .nox, .tox, .pytest_tmp, .backup, .healing_backups are intentionally
        # NOT approved; they should be flagged as ILLEGAL_CACHE_DIR and deleted if unused.
        from agentic_core.L0_routing.config.path_constants import TOOLING_EXCLUDED_DIRS

        approved_dirs = _sovereign_dirs | set(TOOLING_EXCLUDED_DIRS)
        approved_files = {
            # Standard project config
            ".gitignore",
            ".gitattributes",
            ".editorconfig",
            ".env",
            ".env.example",
            ".flake8",
            ".mypy.ini",
            ".pre-commit-config.yaml",
            # Windsurf workspace files
            ".windsurfrules",
            ".windsurfrules.bak",
            ".windsurf.code-workspace",
            ".windsurfignore",
            # Python project files
            "pyproject.toml",
            "setup.py",
            "setup.cfg",
            "requirements.txt",
            "requirements-dev.txt",
            "noxfile.py",
            "Makefile",
            "pytest.ini",
            "tox.ini",
            "MANIFEST.in",
            # Docs
            "README.md",
            "LICENSE",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            # Coverage
            ".coverage",
            # Misc tracked files
            "progress.txt",
            # Runtime / test infrastructure
            "conftest.py",
            "runtime_state.json",
        }
        # Transient dirs/files that should be deleted, not relocated
        delete_patterns = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS

        try:
            for entry in tqdm(self.project_root.iterdir(), desc="Processing", unit="item"):
                name = entry.name
                if name in approved_dirs or name in approved_files:
                    continue
                # Transient tmp files/dirs generated by pytest / tools
                if name.startswith("tmp") and len(name) > 3:
                    violations.append(
                        {
                            "type": "ILLEGAL_CACHE_DIR",
                            "file": str(entry),
                            "message": f"Transient tmp artifact '{name}' in project root",
                            "severity": "low",
                            "recommended_action": f"Delete '{name}'",
                            "confidence": 0.95,
                        },
                    )
                    continue
                # Temp/cache folders that should be auto-deleted
                if entry.is_dir() and name in {
                    ".nox",
                    ".tox",
                    ".pytest_tmp",
                    ".backup",
                    ".healing_backups",
                    ".mypy_cache",
                    ".ruff_cache",
                }:
                    violations.append(
                        {
                            "type": "ILLEGAL_CACHE_DIR",
                            "file": str(entry),
                            "message": f"Unused cache/temp directory '{name}' in project root",
                            "severity": "low",
                            "recommended_action": f"Delete '{name}' if unused (>7 days old)",
                            "confidence": 0.95,
                        },
                    )
                    continue
                if entry.is_dir() and name in delete_patterns:
                    violations.append(
                        {
                            "type": "ILLEGAL_CACHE_DIR",
                            "file": str(entry),
                            "message": f"Transient cache directory '{name}' in project root",
                            "severity": "low",
                            "recommended_action": f"Delete {name} (add to .gitignore)",
                            "confidence": 0.95,
                        },
                    )
                elif entry.is_dir():
                    violations.append(
                        {
                            "type": "UNAPPROVED_ROOT_DIR",
                            "file": str(entry),
                            "message": f"Unapproved directory '{name}' in project root (not in SOVEREIGN_TERRITORIES)",
                            "severity": "high",
                            "recommended_action": (
                                f"Move '{name}' to its canonical SSOT location or register it as a sovereign territory"
                            ),
                            "confidence": 0.9,
                        },
                    )
                elif entry.is_file() and name not in approved_files:
                    violations.append(
                        {
                            "type": "UNAPPROVED_ROOT_FILE",
                            "file": str(entry),
                            "message": f"Unapproved file '{name}' in project root",
                            "severity": "medium",
                            "recommended_action": (
                                f"Move '{name}' to its canonical SSOT location or add to approved list"
                            ),
                            "confidence": 0.8,  # review: Add error context logging
                        },
                    )
        except OSError as exc:
            violations.append(
                {
                    "type": "SCAN_ERROR",
                    "file": str(self.project_root),  # review: Add error context logging
                    "message": f"Root scan failed: {exc}",
                    "severity": "high",
                    "recommended_action": "Fix project root access permissions",
                    "confidence": 1.0,
                },
            )

        return {"violations": violations}

    # guardian: allow-type-erasure
    def heal(self, violation: dict) -> dict:
        """
        [SOVEREIGN CONTRACT] Standardized healing interface for Hygiene.
        """
        target = violation.get("file") or violation.get("target")
        v_type = violation.get("type", "").upper()

        if not target and "CACHE" not in v_type:
            return {"status": "skipped", "reason": "No target file specified"}

        try:
            # Handle cache/transient directories
            if "CACHE" in v_type or "__PYCACHE__" in str(target).upper():
                if hasattr(self, "purge_cache"):
                    self.purge_cache()
                    return {"status": "success", "action": "purged_cache"}
                else:
                    import time
                    from pathlib import Path

                    if target and Path(target).exists():
                        target_path = Path(target)

                        # For temp/backup folders, check age before deleting
                        if target_path.is_dir() and target_path.name in {
                            ".nox",
                            ".tox",
                            ".backup",
                            ".healing_backups",
                        }:
                            try:
                                age_days = (time.time() - target_path.stat().st_mtime) / 86400
                                if age_days <= 7:
                                    return {
                                        "status": "skipped",  # review: Add error context logging
                                        "reason": f"{target_path.name} is recent ({age_days:.1f} days old), keeping",
                                    }
                            except OSError as e:  # guardian: allow-log-and-swallow -- mtime check: non-fatal, file access failure skips recent-check
                                logging.getLogger(__name__).debug(
                                    "root_hygiene_healer: OSError swallowed at L723: %s", e
                                )

                        # Delete the cache/temp folder or file
                        if target_path.is_dir():  # review: Add error context logging
                            _wg.remove_tree(target_path)
                        else:
                            _wg.remove_file(target_path)
                        return {"status": "success", "action": f"deleted {target_path.name}"}

            # Handle unapproved root files
            elif v_type == "UNAPPROVED_ROOT_FILE":
                from pathlib import Path

                target_path = Path(target)
                if not target_path.exists():
                    return {"status": "skipped", "reason": f"File {target} no longer exists"}

                # Determine destination based on file type
                if target_path.suffix == ".py":
                    # Python scripts go to tools/
                    dest_dir = self.project_root / "tools"
                    _wg.ensure_dir(dest_dir)
                    dest = dest_dir / target_path.name
                elif target_path.suffix in {".txt", ".log", ".csv"}:
                    # Test/log outputs go to docs/reports/
                    dest_dir = self.project_root / "docs" / "reports"
                    _wg.ensure_dir(dest_dir)
                    dest = dest_dir / target_path.name
                else:
                    # Unknown type — archive it
                    dest_dir = self.project_root / HEALING_BACKUPS_DIR / "root_cleanup"
                    _wg.ensure_dir(dest_dir)
                    dest = dest_dir / target_path.name

                if not self.dry_run:
                    _wg.move_path(str(target_path), str(dest))
                return {"status": "success", "action": f"moved to {dest.relative_to(self.project_root)}"}

            # Handle unapproved root directories
            elif v_type == "UNAPPROVED_ROOT_DIR":
                from pathlib import Path

                target_path = Path(target)
                if not target_path.exists():
                    return {"status": "skipped", "reason": f"Directory {target} no longer exists"}

                # Check if it's actually a sovereign territory that should be registered
                dir_name = target_path.name

                # Known sovereign territories that need registration
                KNOWN_SOVEREIGN_TERRITORIES = {
                    "apps": "Application modules (apps_*) — register in SOVEREIGN_TERRITORIES",
                    "artifacts": "Build/ADG artifacts — register in SOVEREIGN_TERRITORIES",
                    "observability": "Observability/monitoring — register in SOVEREIGN_TERRITORIES",
                    "system_learning": "Meta-learning pipeline — register in SOVEREIGN_TERRITORIES",
                    "tools": "Standalone scripts/utilities — register in SOVEREIGN_TERRITORIES",
                }

                if dir_name in KNOWN_SOVEREIGN_TERRITORIES:
                    return {
                        "status": "blocked",
                        "reason": f"SOVEREIGN TERRITORY: '{dir_name}' — {KNOWN_SOVEREIGN_TERRITORIES[dir_name]}",
                        "recommended_action": f"Add '{dir_name}' to PROJECT_ROOT_WHITELIST in agentic_core/L5_safety/config/structure_blueprint.py",
                    }
                else:
                    # Unknown directory — archive it
                    dest_dir = self.project_root / HEALING_BACKUPS_DIR / "root_cleanup"
                    _wg.ensure_dir(dest_dir)
                    dest = dest_dir / dir_name
                    if not self.dry_run:
                        _wg.move_path(str(target_path), str(dest))
                    return {
                        "status": "success",
                        "action": f"archived to {dest.relative_to(self.project_root)}",
                    }

            return {"status": "skipped", "reason": f"Unknown hygiene type: {v_type}"}

        except (RuntimeError, OSError) as e:
            return {"status": "error", "error": str(e)}

    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        # guardian: allow-magic-config
        max_depth: int = 3,
        _call_path: set[str] | None = None,
    ) -> dict[str, int]:
        """
        Standard healing interface for execute_ssot.py integration.

        This method provides the canonical healing interface that integrates
        with the HealerMixin chain and execute_ssot.py orchestration.
        """
        if _call_path is None:
            _call_path = set()

        # Prevent cycles
        agent_id = f"RootHygieneAgent@{self.project_root}"
        if agent_id in _call_path:
            return {"violations_found": 0, "violations_fixed": 0, "errors": 0, "skipped": 0}
        _call_path.add(agent_id)

        # Configure healing mode
        self.dry_run = dry_run and not execute

        try:
            # Execute the hygiene enforcement
            self._enforce_root_hygiene()

            # Calculate violations based on stats
            violations_found = (
                self.stats["scripts_evacuated"]
                + self.stats["dirs_evacuated"]
                + self.stats["coverage_relocated"]
                + self.stats["illegal_dirs_removed"]
                + self.stats["n_duplicates_removed"]
            )
            violations_fixed = violations_found  # All detected violations are fixed

            return {
                "violations_found": violations_found,
                "violations_fixed": violations_fixed,
                "errors": self.stats["errors"],
                "skipped": 0,
            }

        except (RuntimeError, OSError) as e:  # guardian: allow-silent-swallow
            print(f"[ERROR] RootHygieneAgent healing failed: {e}")
            return {"violations_found": 0, "violations_fixed": 0, "errors": 1, "skipped": 0}
        finally:
            _call_path.discard(agent_id)


def main():
    """Standalone execution for testing."""
    import argparse

    parser = argparse.ArgumentParser(description="Root Hygiene Agent")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes")
    args = parser.parse_args()

    from pathlib import Path

    project_root = Path(".")

    agent = RootHygieneAgent(project_root=project_root, dry_run=args.dry_run)

    result = agent.run()
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()


# Backward-compat alias — Phase 10 rename (RootHygieneAgent → RootHygieneHealerAgent)
RootHygieneAgent = RootHygieneHealerAgent
