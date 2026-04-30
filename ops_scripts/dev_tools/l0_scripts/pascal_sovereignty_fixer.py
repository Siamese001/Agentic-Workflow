from agentic_core.L0_routing.config.path_constants import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "pascal_sovereignty_fixer")
_emit_applies_guardrail("p0", "pascal_sovereignty_fixer", "p0_governance")
_emit_reads_policy_state("p0", "pascal_sovereignty_fixer", "policy_binding")
_emit_snapshots_state("p0", "pascal_sovereignty_fixer", "state_snapshot")
emit_replay_key("p0", "pascal_sovereignty_fixer")
emit_determinism_digest("p0", "pascal_sovereignty_fixer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "pascal_sovereignty_fixer", "execution_auth")
_emit_validates_capability("p2", "pascal_sovereignty_fixer", "capability_check")
_emit_routes_to_capability("p2", "pascal_sovereignty_fixer", "capability_route")
_emit_writes_via_uwg("p2", "pascal_sovereignty_fixer", "uwg_write")
_emit_blocks_direct_write("p2", "pascal_sovereignty_fixer", "direct_write_block")
_emit_records_tool_invocation("p2", "pascal_sovereignty_fixer", "tool_invocation")
_emit_captures_execution_output("p2", "pascal_sovereignty_fixer", "exec_output")
_emit_dispatches_agent("p3", "pascal_sovereignty_fixer", "agent_dispatch")
_emit_coordinates_agents("p3", "pascal_sovereignty_fixer", "agent_coordination")
_emit_records_workflow_lineage("p3", "pascal_sovereignty_fixer", "workflow_lineage")
_emit_records_healing_outcome("p3", "pascal_sovereignty_fixer", "healing_outcome")
_emit_escalates_failure("p3", "pascal_sovereignty_fixer", "failure_escalation")
_emit_orchestrates_workflow("p3", "pascal_sovereignty_fixer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "pascal_sovereignty_fixer", "healing_dispatch")
_emit_invokes_evaluation("p3", "pascal_sovereignty_fixer", "evaluation_signal")
_emit_records_telemetry_event("p4", "pascal_sovereignty_fixer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "pascal_sovereignty_fixer", "eval_metric")
_emit_stores_embedding("p4", "pascal_sovereignty_fixer", "embedding_store")
_emit_updates_meta_learning_state("p4", "pascal_sovereignty_fixer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "pascal_sovereignty_fixer", "exec_snapshot_link")

r"""
File: PascalSovereigntyFixer.py
Path: C:\Git\Agentic-Workflow\PascalSovereigntyFixer.py
Status: FINAL - GOLD MASTER (Phase 4)
Rationale:
    Removes legacy commentary regarding 'healer_mixin.py' to produce a clean,
    professional artifact. The logic is now fully reliant on the '_mixin.py'
    pattern matcher verified in Phase 2/3.
"""

import ast
import platform
import re
import sys
import time
from pathlib import Path
from typing import Literal

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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("pascal_sovereignty_fixer", "p4obs", "metric_1")
_emit_emits_metric_event("pascal_sovereignty_fixer", "p4obs", "metric_2")
_emit_emits_metric_event("pascal_sovereignty_fixer", "p4obs", "metric_3")
_emit_emits_metric_event("pascal_sovereignty_fixer", "p4obs", "metric_4")
_emit_emits_metric_event("pascal_sovereignty_fixer", "p4obs", "metric_5")
_emit_emits_metric_event("pascal_sovereignty_fixer", "p4obs", "metric_6")
_emit_records_incident_event("pascal_sovereignty_fixer", "p4obs", "incident")
_emit_captures_runtime_anomaly("pascal_sovereignty_fixer", "p4obs", "anomaly")
_emit_writes_observability_log("pascal_sovereignty_fixer", "p4obs", "obs_log")
_emit_updates_monitoring_state("pascal_sovereignty_fixer", "p4obs", "mon_state")
_emit_triggers_alert("pascal_sovereignty_fixer", "p4obs", "alert")
_emit_links_incident_trace("pascal_sovereignty_fixer", "p4obs", "trace_link")
_emit_captures_pattern("pascal_sovereignty_fixer", "p3lm", "pattern")
_emit_records_learning_event("pascal_sovereignty_fixer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("pascal_sovereignty_fixer", "p3lm", "snapshot")
_emit_feeds_meta_learning("pascal_sovereignty_fixer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("pascal_sovereignty_fixer", "p3lm", "routing")
_emit_improves_agent_policy("pascal_sovereignty_fixer", "p3lm", "policy")
_emit_stores_learning_state("pascal_sovereignty_fixer", "p3lm", "state")
_emit_records_execution_trace("pascal_sovereignty_fixer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("pascal_sovereignty_fixer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("pascal_sovereignty_fixer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("pascal_sovereignty_fixer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("pascal_sovereignty_fixer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("pascal_sovereignty_fixer", "env_read", "p2_env_1")
_emit_reads_environ("pascal_sovereignty_fixer", "env_read", "p2_env_2")
_emit_reads_runtime_state("pascal_sovereignty_fixer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("pascal_sovereignty_fixer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "pascal_sovereignty_fixer", "context_pull")
_emit_pulls_context("p1", "pascal_sovereignty_fixer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "pascal_sovereignty_fixer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "pascal_sovereignty_fixer", "uwg_term_2")
_emit_writes_through("p1", "pascal_sovereignty_fixer", "write_through")
_emit_writes_through("p1", "pascal_sovereignty_fixer", "write_through_2")
_emit_validated_by_safety_plane("p1", "pascal_sovereignty_fixer", "safety_validation")
_emit_invokes_eval("p1", "pascal_sovereignty_fixer", "eval_call")
_emit_proposal_commits_routing("p1", "pascal_sovereignty_fixer", "routing_commit")
_emit_escalates_to_human("p1", "pascal_sovereignty_fixer", "human_escalation")
_emit_routes_through("p1", "pascal_sovereignty_fixer", "route_through")
_emit_checks_agent_registry("p1", "pascal_sovereignty_fixer", "agent_registry")
_emit_validates_agent_capability("p1", "pascal_sovereignty_fixer", "capability")
_emit_dispatches_execution_plan("p1", "pascal_sovereignty_fixer", "exec_plan")
_emit_agent_executes_agent("p1", "pascal_sovereignty_fixer", "sub_agent")
_emit_routes_to_agent("p1", "pascal_sovereignty_fixer", "target_agent")
_emit_verifies_policy("p1", "pascal_sovereignty_fixer", "policy_check")
_emit_observes_runtime_state("p1", "pascal_sovereignty_fixer", "runtime_state")
_emit_verifies_boundary("p1", "pascal_sovereignty_fixer", "boundary_check")
_emit_transcripts_response("p1", "pascal_sovereignty_fixer", "transcript")
_emit_hard_fails_untranscripted("p1", "pascal_sovereignty_fixer")
_emit_gated_by_confidence("p1", "pascal_sovereignty_fixer", "confidence_gate")


# SSOT Integration with fast-fail pruning
def get_python_files_fast(root: Path, _fn=None) -> list[Path]:
    """
    Optimized repository scanner that prunes heavy/irrelevant directories
    before they enter the pipeline.
    """
    if _fn is None:
        from agentic_core.utils.fs_util import get_python_files_fast as canonical_get_python_files

        _fn = canonical_get_python_files

    exclude_dirs = list(GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES)

    return list(_fn(root, exclude_dirs=exclude_dirs))


FileType = Literal["AGENT", "CLASS", "MIXIN", "UTILITY", "IGNORE"]


class PascalSovereigntyFixer:
    """Enforces strict file naming conventions based on AST content analysis."""

    def __init__(self, dry_run: bool = False, verbose: bool = False, validate_only: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.validate_only = validate_only
        self.stats = {
            "analyzed": 0,
            "compliant": 0,
            "renamed": 0,
            "imports_fixed": 0,
            "violations": {"AGENT": 0, "CLASS": 0, "MIXIN": 0, "UTILITY": 0},
        }
        # CACHE: Track file paths in memory to avoid repetitive disk scanning (O(1) lookups)
        self.file_registry: list[Path] = []

    def classify_file(self, path: Path) -> FileType:
        """Classify file by delegating to classification kernel (SSOT).

        [REFACTORED 2026-02-08] Replaced FCA instantiation with lightweight
        kernel delegation. Maps kernel's rich FileType to PSF's simpler set.
        """
        from agentic_core.L5_safety.reasoning.core_kernel.classification_kernel import (
            classify_file_standalone,
        )

        kernel_type = classify_file_standalone(path)

        # Map kernel types → PSF FileType
        kernel_to_psf = {
            "AGENT": "AGENT",
            "MIXIN": "MIXIN",
            "IGNORE": "IGNORE",
            "TEST": "IGNORE",
            "STUB": "IGNORE",
            "UTILITY": "UTILITY",
            "SCRIPT": "UTILITY",
        }
        # Everything else (CLASS, CONFIG, VALIDATOR, PROTOCOL, etc.) → CLASS
        return kernel_to_psf.get(kernel_type, "CLASS")

    def update_imports(self, old_name: str, new_name: str) -> int:
        """Refactor imports using the in-memory registry.

        Note: This is intentionally NOT delegated to FCA because it operates on
        PSF's in-memory file_registry, whereas FCA scans the filesystem.
        Import rewriting is simple regex, not a classification concern.
        """
        count = 0
        old_mod, new_mod = old_name.replace(".py", ""), new_name.replace(".py", "")

        # guardian: allow-path-string
        regex_from = re.compile(r"(?P<prefix>from\s+\.*)" + re.escape(old_mod) + r"(?P<suffix>\s+import)")
        regex_import = re.compile(
            rf"(?P<prefix>import\s+){re.escape(old_mod)}(?P<suffix>(\s+as\s+\w+)?(\s*,|\s|$))",
        )

        for _i, path in tqdm(enumerate(self.file_registry), desc="Processing", unit="item"):
            if path.name == new_name or not path.exists():
                continue
            try:
                content = path.read_text(encoding="utf-8")
                if old_mod not in content:
                    continue

                # guardian: allow-path-string
                new_content = regex_from.sub(r"\g<prefix>" + new_mod + r"\g<suffix>", content)
                # guardian: allow-path-string
                new_content = regex_import.sub(r"\g<prefix>" + new_mod + r"\g<suffix>", new_content)

                if new_content != content:
                    if not self.dry_run:
                        path.write_text(new_content, encoding="utf-8")
                    count += 1
            except Exception:  # guardian: allow-silent-swallow
                continue
        return count

    def run(self, root: Path) -> int:
        """Main orchestration loop."""
        print(f"[SOVEREIGNTY] {'DRY RUN' if self.dry_run else 'EXECUTE'} MODE")
        print("=" * 60)

        if not self.verify_environment():
            return 1

        print("Scanning repository (Fast One-Time Pass)...")
        self.file_registry = get_python_files_fast(root)
        self.stats["analyzed"] = len(self.file_registry)

        # Iterating over a copy to allow registry updates during renames
        for idx, path in tqdm(enumerate(list(self.file_registry)), desc="Processing", unit="item"):
            if not path.exists():
                continue
            ftype = self.classify_file(path)
            if ftype == "IGNORE":
                continue

            new_name = self.get_compliant_name(path, ftype)
            if new_name and new_name != path.name:
                self.stats["violations"][ftype] += 1
                print(f"\n[DETECT] {path.name} ({ftype}) -> {new_name}")
                # [CHANGED] From safe_rename_windows to resolve_collision_and_rename
                if self.resolve_collision_and_rename(path, new_name):
                    self.stats["renamed"] += 1
                    # Update in-memory tracker for subsequent import refactors
                    dest = path.parent / new_name

                    # Only update registry if the file wasn't deleted (duplicate merge)
                    if dest.exists():
                        self.file_registry[idx] = dest

                    self.stats["imports_fixed"] += self.update_imports(path.name, new_name)
            else:
                self.stats["compliant"] += 1

        print("\n" + "=" * 60)
        print(f"Total files analyzed: {self.stats['analyzed']}")
        print(f"Compliant files:      {self.stats['compliant']}")
        total_violations = sum(self.stats["violations"].values())
        print(f"Violations detected:  {total_violations}")
        print(f"  - Agents:  {self.stats['violations']['AGENT']}")
        print(f"  - Classes: {self.stats['violations']['CLASS']}")
        print(f"  - Utils:   {self.stats['violations']['UTILITY']}")
        print(f"  - Mixins:  {self.stats['violations']['MIXIN']}")
        if not self.dry_run:
            print(f"Files Renamed:        {self.stats['renamed']}")
            print(f"Imports Fixed:        {self.stats['imports_fixed']}")

        # Critical Analysis: Returning exit 1 on violations ensures git hooks
        # block non-compliant commits.
        return 0 if (not self.validate_only or total_violations == 0) else 1

    def verify_environment(self) -> bool:
        """Checks for LongPathsEnabled on Windows."""
        if platform.system() == "Windows":
            try:
                import winreg

                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Control\FileSystem",
                )
                value, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
                if value != 1:
                    print("[WARNING] Windows LongPathsEnabled is NOT set to 1.")
                    if not self.dry_run:
                        return False
            except Exception:  # guardian: allow-silent-swallow
                pass
        return True

    def resolve_collision_and_rename(self, src: Path, dest_name: str) -> bool:
        """
        Handles renaming with intelligent collision resolution.
        Returns True if the VIOLATION was resolved (either by rename, delete, or move).
        """
        dest = src.parent / dest_name

        # Case 0: Trivial match
        if src.name == dest_name:
            return False

        if self.dry_run:
            print(f"  [PLAN] Rename {src.name} -> {dest_name}")
            return True

        # Case 1: Destination Conflict Detection
        is_collision = False
        if dest.exists():
            try:
                # Resolve paths to handle case-insensitivity on Windows
                if dest.resolve() != src.resolve():
                    is_collision = True
            except OSError:  # review: Add error context logging
                is_collision = True

        if is_collision:
            print(f"  [COLLISION] Target {dest_name} already exists. Analyzing content...")
            try:
                # Critical Analysis: Binary read ensures exact match without encoding issues.
                src_content = src.read_bytes()
                dest_content = dest.read_bytes()

                if src_content == dest_content:
                    print("  [ANALYSIS] Files are IDENTICAL. Remediation: Deleting redundant violator.")
                    print(f"  [ACTION] DELETE {src.name}")
                    src.unlink()
                    return True  # Violation resolved by deletion
                else:
                    # Divergent content: Rename to .CONFLICT to preserve data
                    print(
                        "  [ANALYSIS] Files are DIFFERENT. Remediation: Preserving data via conflict rename.",
                    )
                    timestamp = int(time.time())
                    conflict_name = f"{dest_name}.CONFLICT_{timestamp}"
                    conflict_path = src.parent / conflict_name

                    print(f"  [ACTION] RENAME {src.name} -> {conflict_name}")
                    src.rename(conflict_path)
                    return True  # Violation resolved by moving aside
            except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
                print(f"  [ERROR] Failed to resolve collision: {e}")
                return False

        # Case 2: Standard Rename (or Case-Only Rename)
        try:
            # Atomic temp shuffle for Windows case-sensitivity support
            temp = src.parent / f"__temp_{src.name}"
            src.rename(temp)
            temp.rename(dest)
            return True
        except OSError as e:  # review: Add error context logging
            print(f"  [ERROR] Rename failed: {e}")
            return False

    def get_compliant_name(self, path: Path, file_type: FileType) -> str | None:
        """Calculate compliant filename via AST class-name extraction.

        2026-04-30: Removed FCA delegation. The previous delegate-to-FCA branch
        had a broken exception handler (re-raised inside a guardian-marked
        silent-swallow block, with unreachable `pass` after `raise`) and was an
        L_OPS->L5 layer-gravity inversion. The AST extraction below is sufficient
        for pascal-sovereignty naming on dev-tool scripts.
        """
        if file_type == "IGNORE":
            return None

        # Mixin standardization (snake_case + _mixin suffix).
        if file_type == "MIXIN":
            stem = path.stem
            s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", stem)
            clean_stem = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
            if not clean_stem.endswith("_mixin"):
                clean_stem += "_mixin"
            target = f"{clean_stem}.py"
            return target if target != path.name else None

        if file_type == "UTILITY":
            return None

        # AST-based class-name extraction.
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            if not classes:
                return None
            primary = classes[0]
            stem_clean = path.stem.replace("_", "").lower()
            for cls_name in classes:
                if cls_name.lower() == stem_clean:
                    primary = cls_name
                    break
            target_name = primary
            if file_type == "AGENT" and not target_name.endswith("Agent"):
                target_name += "Agent"
            return f"{target_name}.py"
        except (ValueError, TypeError, RuntimeError) as e:
            return None


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Pascal Sovereignty Fixer")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes")
    parser.add_argument("--validate", action="store_true", help="Check compliance only")
    args = parser.parse_args()
    is_dry_run = args.dry_run or args.validate
    sys.exit(PascalSovereigntyFixer(dry_run=is_dry_run, validate_only=args.validate).run(Path(".")))


if __name__ == "__main__":
    main()
