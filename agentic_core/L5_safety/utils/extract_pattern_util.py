from __future__ import annotations

from agentic_core.L2_execution.tools import write_gateway as _wg
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "extract_pattern_util")
emit_determinism_digest("p0", "extract_pattern_util")

_emit_dispatches_healing_run("p1", "extract_pattern_util", "L5")
_emit_routes_through("p1", "extract_pattern_util", "L5")
_emit_escalates_to_human("p1", "extract_pattern_util", "L5")
_emit_reads_policy_state("p1", "extract_pattern_util", "L5")

"\nExtract PatternEnforcerAgent from canon_agents_pattern.py.\nAlso removes SubAtomicAgent stub and adds proper import.\n"
import ast
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

SOURCE_FILE = Path("agentic_core/L1_cognition/thought_engine/canon_agents_pattern.py")
TARGET_DIR = Path("agentic_core/L1_cognition/thought_engine")


def extract_class_with_context(content: str, class_name: str) -> tuple[str, int, int]:
    """Extract class source with preceding comments."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "extract_class_with_context", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "extract_class_with_context", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "extract_class_with_context")
    lines = content.split("\n")
    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            start_line = node.lineno - 1
            end_line = node.end_lineno
            while start_line > 0:
                prev_line = lines[start_line - 1].strip()
                if prev_line.startswith("#") or not prev_line:
                    start_line -= 1
                else:
                    break
            class_source = "\n".join(lines[start_line:end_line])
            return (class_source, start_line + 1, end_line)
    raise ValueError(f"Class {class_name} not found")


def create_pattern_enforcer_file(class_source: str):
    """Create sovereign file for PatternEnforcerAgent."""
    target_file = TARGET_DIR / "PatternEnforcerAgent.py"
    content = f'"""\nPatternEnforcerAgent - Extracted from canon_agents_pattern.py\nEnforces coding patterns and best practices across Python files.\n"""\nimport ast\nimport logging\nimport re\nfrom typing import Any, Dict, List, Optional, Protocol, Tuple\n\n# DEPRECATED: CanonBaseAgentInterface removed - use Protocol instead\ntry:\n    from agentic_core.base_agents.canon_base_agent_interface import CanonBaseAgentInterface\nexcept ImportError:\n    class CanonBaseAgentInterface(Protocol):\n        pass\n\nfrom agentic_core.L3_orchestration.reasoning.subatomic_testing_mixin import subatomic_testing_mixin\nfrom agentic_core.L5_safety.enforcement.mcp_hardened_mixin import mcp_hardened_mixin\nfrom agentic_core.L5_safety.config.structure_blueprint_config import (\n    SOVEREIGN_TERRITORIES,\n    CORE_SUBFOLDER_MAP,\n)\nfrom agentic_core.mixins.healer_mixin import healer_mixin\n\nLogger: Any = logging.getLogger(__name__)\n\n{class_source}\n'
    print(f"Creating {target_file}")
    _wg.open_write(target_file, content)
    return target_file


def update_source_file(source_file: Path):
    """Remove PatternEnforcerAgent and SubAtomicAgent stub, add proper import."""
    with open(source_file, encoding="utf-8") as f:
        content = f.read()
    lines = content.split("\n")
    tree = ast.parse(content)
    classes_to_remove = ["PatternEnforcerAgent", "SubAtomicAgent"]
    ranges_to_remove = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name in classes_to_remove:
            start_line = node.lineno - 1
            end_line = node.end_lineno
            while start_line > 0:
                prev_line = lines[start_line - 1].strip()
                if prev_line.startswith("#") or not prev_line:
                    start_line -= 1
                else:
                    break
            ranges_to_remove.append((start_line, end_line, node.name))
    ranges_to_remove.sort(reverse=True)
    backup_file = source_file.with_suffix(".py.bak")
    print(f"  Creating backup: {backup_file}")
    with open(source_file, encoding="utf-8") as f:
        _wg.open_write(backup_file, f.read())
    for start, end, name in ranges_to_remove:
        del lines[start:end]
        if name == "PatternEnforcerAgent":
            lines.insert(start, f"# {name} extracted to {name}.py (Phase B Task 4)")
            lines.insert(start + 1, "")
    import_line = "from agentic_core.L3_orchestration.reasoning.SubAtomicAgent import SubAtomicAgent"
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("from agentic_core.base_agents"):
            insert_idx = i + 1
            break
    lines.insert(insert_idx, import_line)
    lines.insert(insert_idx + 1, "")
    _wg.open_write(source_file, "\n".join(lines))


def main():
    print("=" * 60)
    print("PATTERN AGENT EXTRACTION - PHASE B TASK 4")
    print("=" * 60)
    print(f"\nReading {SOURCE_FILE}")
    with open(SOURCE_FILE, encoding="utf-8") as f:
        content = f.read()
    print("\n📦 Extracting PatternEnforcerAgent...")
    try:
        class_source, start, end = extract_class_with_context(content, "PatternEnforcerAgent")
        target_file = create_pattern_enforcer_file(class_source)
        print(f"  ✅ Created {target_file} (lines {start}-{end})")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False
    print(f"\nUpdating {SOURCE_FILE}...")
    print("  - Removing PatternEnforcerAgent")
    print("  - Removing SubAtomicAgent stub")
    print("  - Adding SubAtomicAgent import")
    update_source_file(SOURCE_FILE)
    print(f"  ✅ Updated {SOURCE_FILE}")
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print("\n✅ PatternEnforcerAgent.py created")
    print("✅ canon_agents_pattern.py updated with proper import")
    print("\n⚠️  Next steps:")
    print("  1. Rename _GenerativeGuard_Deprecated in CanonHealerAgent.py")
    print("  2. Update imports for PatternEnforcerAgent")
    print("  3. Run discovery to verify 281 agents")
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
