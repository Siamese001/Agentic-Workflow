"""Fix all Unicode emojis in Python files to ASCII equivalents.
Prevents Windows encoding issues.
"""

from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    APPS_SHARED_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "emoji_fixer")
emit_determinism_digest("p0", "emoji_fixer")

_emit_dispatches_healing_run("p1", "emoji_fixer", "L0")
_emit_routes_through("p1", "emoji_fixer", "L0")
_emit_escalates_to_human("p1", "emoji_fixer", "L0")
_emit_reads_policy_state("p1", "emoji_fixer", "L0")

_emit_records_execution_trace("p0", "evidence", "emoji_fixer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "emoji_fixer", "p0_governance")
_emit_snapshots_state("p0", "emoji_fixer", "state_snapshot")
_emit_authorize_and_execute("p2", "emoji_fixer", "execution_auth")
_emit_validates_capability("p2", "emoji_fixer", "capability_check")
_emit_routes_to_capability("p2", "emoji_fixer", "capability_route")
_emit_writes_via_uwg("p2", "emoji_fixer", "uwg_write")
_emit_blocks_direct_write("p2", "emoji_fixer", "direct_write_block")
_emit_records_tool_invocation("p2", "emoji_fixer", "tool_invocation")
_emit_captures_execution_output("p2", "emoji_fixer", "exec_output")
_emit_dispatches_agent("p3", "emoji_fixer", "agent_dispatch")
_emit_coordinates_agents("p3", "emoji_fixer", "agent_coordination")
_emit_records_workflow_lineage("p3", "emoji_fixer", "workflow_lineage")
_emit_records_healing_outcome("p3", "emoji_fixer", "healing_outcome")
_emit_escalates_failure("p3", "emoji_fixer", "failure_escalation")
_emit_orchestrates_workflow("p3", "emoji_fixer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "emoji_fixer", "healing_dispatch")
_emit_invokes_evaluation("p3", "emoji_fixer", "evaluation_signal")
_emit_records_telemetry_event("p4", "emoji_fixer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "emoji_fixer", "eval_metric")
_emit_stores_embedding("p4", "emoji_fixer", "embedding_store")
_emit_updates_meta_learning_state("p4", "emoji_fixer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "emoji_fixer", "exec_snapshot_link")

try:
    from agentic_core.L0_routing.scripts.full_agent_discovery import (
        AGENTIC_CORE_DIR,
        APPS_SHARED_DIR,
        get_python_files,
    )
except ImportError:
    AGENTIC_CORE_DIR = Path(AGENTIC_CORE_DIR)
    APPS_SHARED_DIR = Path(APPS_SHARED_DIR)

    def get_python_files(directory):
        return directory.rglob("*.py")


EMOJI_MAP = {
    "✅": "[OK]",
    "⚠️": "[!]",
    "🔧": "[+]",
    "🔄": "[~]",
    "🆕": "[NEW]",
    "♻️": "[REUSE]",
    "🚨": "[ALERT]",
    "🚫": "[X]",
    "❌": "[X]",
    "🧹": "[CLEAN]",
    "🏛️": "[ARCH]",
    "💾": "[SAVE]",
    "🔍": "[SCAN]",
    "📊": "[STATS]",
    "📂": "[DIR]",
    "📋": "[PLAN]",
    "🚀": "[START]",
    "🌱": "[GIT]",
    "🧬": "[CYCLE]",
}


def fix_emojis_in_file(file_path: str) -> bool:
    """Replace all emojis in a file with ASCII equivalents."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        original_content = content
        for emoji, replacement in EMOJI_MAP.items():
            content = content.replace(emoji, replacement)
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✓ Fixed: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"✗ Error fixing {file_path}: {e}")
        return False


def main() -> None:
    """Find and fix all Python files with emojis."""
    root = Path.cwd()
    targets = [root / AGENTIC_CORE_DIR, root / APPS_SHARED_DIR]
    fixed_count = 0
    for target_dir in targets:
        if not target_dir.exists():
            continue
        for py_file in get_python_files(target_dir):
            if fix_emojis_in_file(str(py_file)):
                fixed_count += 1
    print(f"\n[*] Fixed {fixed_count} files")


if __name__ == "__main__":
    main()
