"""
Find REAL duplicate agent files by NAME (not content hash).
Shows files with same name in different locations.
"""

from collections import defaultdict
from datetime import datetime
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "find_real_duplicates_v2_util")
emit_determinism_digest("p0", "find_real_duplicates_v2_util")

_emit_dispatches_healing_run("p1", "find_real_duplicates_v2_util", "L0")
_emit_routes_through("p1", "find_real_duplicates_v2_util", "L0")
_emit_escalates_to_human("p1", "find_real_duplicates_v2_util", "L0")
_emit_reads_policy_state("p1", "find_real_duplicates_v2_util", "L0")


def is_agent_file(path: Path) -> bool:
    """Check if path is an actual agent file (not test).

    [REFACTORED 2026-02-08] Aligned with classification kernel naming rules.
    For full AST-based classification, use:
        from agentic_core.L5_safety.core_kernel.classification_kernel import is_agent_file
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "is_agent_file", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "is_agent_file", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "is_agent_file")
    if not path.name.endswith("Agent.py"):
        return False
    path_str = str(path).lower()
    if "test" in path_str or "\\tests\\" in path_str or "/tests/" in path_str:
        return False
    if "__pycache__" in path_str or ".venv" in path_str:
        return False
    if "Mixin" in path.name:
        return False
    return True


def get_priority(path: Path, project_root: Path) -> int:
    """Get location priority (lower = better/canonical)."""
    rel_path = str(path.relative_to(project_root)).replace("\\", "/")
    if "blueprint_sovereign" in rel_path:
        return 10
    elif "L5_safety/validators" in rel_path:
        return 2
    elif "L5_safety/agents" in rel_path:
        return 1
    elif rel_path.startswith("agentic_core/"):
        return 3
    else:
        return 5


def infer_rationale(canonical: Path, duplicate: Path, project_root: Path) -> str:
    """Infer rationale based on path patterns."""
    dup_str = str(duplicate.relative_to(project_root))
    can_str = str(canonical.relative_to(project_root))
    if "blueprint_sovereign" in dup_str:
        return "Leftover blueprint template — production version is canonical"
    if "validators" in can_str and "agents" in dup_str or ("agents" in can_str and "validators" in dup_str):
        return "Location overlap: same agent in agents/ vs validators/ directories"
    if "runtime" in dup_str or "runtime" in can_str:
        return "Runtime duplicate — consolidate to primary location"
    return "Exact duplicate — likely copy-paste or migration artifact"


def main():
    project_root = Path.cwd()
    print(f"[SCAN] Searching for agent files in {project_root}...")
    from agentic_core.utils.ssot_discovery_validator import get_agent_files

    agent_files = [f for f in get_agent_files(project_root) if is_agent_file(f)]
    print(f"[SCAN] Found {len(agent_files)} agent files")
    name_to_files = defaultdict(list)
    for file_path in agent_files:
        name_to_files[file_path.name].append(file_path)
    duplicates = {name: files for name, files in name_to_files.items() if len(files) > 1}
    print(f"[FOUND] {len(duplicates)} agent names with multiple locations")
    if not duplicates:
        print("\n✅ No duplicates found!")
        return 0
    output_file = project_root / REPORTS_DIR / "real_duplicates_by_name.md"
    output_file.parent.mkdir(exist_ok=True)
    total_files_to_delete = sum(len(files) - 1 for files in duplicates.values())
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Real Duplicate Agents (By Name)\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Duplicate Agent Names:** {len(duplicates)}\n")
        f.write(f"**Files to Delete:** {total_files_to_delete}\n\n")
        f.write("| Agent Name | Canonical Path | Duplicate Path | Rationale |\n")
        f.write("| --- | --- | --- | --- |\n")
        for agent_name, files in sorted(duplicates.items()):
            files_sorted = sorted(files, key=lambda f: (get_priority(f, project_root), str(f)))
            canonical = files_sorted[0]
            for duplicate in files_sorted[1:]:
                canonical_rel = canonical.relative_to(project_root)
                duplicate_rel = duplicate.relative_to(project_root)
                rationale = infer_rationale(canonical, duplicate, project_root)
                f.write(
                    f"| {agent_name.replace('.py', '')} | `{canonical_rel}` | `{duplicate_rel}` | {rationale} |\n"
                )
        f.write("\n---\n\n")
        f.write("## Delete Commands\n\n")
        f.write("**IMPORTANT:** Review each file before deleting. Use diff to compare:\n")
        f.write("```bash\n")
        f.write('code --diff "canonical_path" "duplicate_path"\n')
        f.write("```\n\n")
        f.write("### Delete Duplicates\n")
        f.write("```bash\n")
        for agent_name, files in sorted(duplicates.items()):
            files_sorted = sorted(files, key=lambda f: (get_priority(f, project_root), str(f)))
            for duplicate in files_sorted[1:]:
                duplicate_rel = duplicate.relative_to(project_root)
                f.write(f'git rm "{duplicate_rel}"\n')
        f.write("```\n")
    print(f"\n✅ Generated: {output_file}")
    print(f"   Duplicate agent names: {len(duplicates)}")
    print(f"   Files to delete: {total_files_to_delete}")
    print("\n" + "=" * 80)
    print("REAL DUPLICATES FOUND (BY NAME)")
    print("=" * 80)
    for agent_name, files in sorted(duplicates.items()):
        files_sorted = sorted(files, key=lambda f: (get_priority(f, project_root), str(f)))
        canonical = files_sorted[0]
        print(f"\n[{agent_name.replace('.py', '')}]")
        print(f"  ✅ KEEP: {canonical.relative_to(project_root)}")
        for duplicate in files_sorted[1:]:
            print(f"  ❌ DELETE: {duplicate.relative_to(project_root)}")
    return 0


if __name__ == "__main__":
    exit(main())
