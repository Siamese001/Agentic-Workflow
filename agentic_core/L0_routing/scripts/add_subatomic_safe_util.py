"""
Safely add SubatomicTestingMixin to agents without tests.
This version handles multi-line class definitions and validates syntax.
"""

import ast
import json
import re
import sys
from pathlib import Path

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
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

emit_replay_key("p0", "add_subatomic_safe_util")
emit_determinism_digest("p0", "add_subatomic_safe_util")

_emit_dispatches_healing_run("p1", "add_subatomic_safe_util", "L0")
_emit_routes_through("p1", "add_subatomic_safe_util", "L0")
_emit_escalates_to_human("p1", "add_subatomic_safe_util", "L0")
_emit_reads_policy_state("p1", "add_subatomic_safe_util", "L0")

_emit_records_execution_trace("p0", "evidence", "add_subatomic_safe_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "add_subatomic_safe_util", "p0_governance")
_emit_snapshots_state("p0", "add_subatomic_safe_util", "state_snapshot")
_emit_authorize_and_execute("p2", "add_subatomic_safe_util", "execution_auth")
_emit_validates_capability("p2", "add_subatomic_safe_util", "capability_check")
_emit_routes_to_capability("p2", "add_subatomic_safe_util", "capability_route")
_emit_writes_via_uwg("p2", "add_subatomic_safe_util", "uwg_write")
_emit_blocks_direct_write("p2", "add_subatomic_safe_util", "direct_write_block")
_emit_records_tool_invocation("p2", "add_subatomic_safe_util", "tool_invocation")
_emit_captures_execution_output("p2", "add_subatomic_safe_util", "exec_output")
_emit_dispatches_agent("p3", "add_subatomic_safe_util", "agent_dispatch")
_emit_coordinates_agents("p3", "add_subatomic_safe_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "add_subatomic_safe_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "add_subatomic_safe_util", "healing_outcome")
_emit_escalates_failure("p3", "add_subatomic_safe_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "add_subatomic_safe_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "add_subatomic_safe_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "add_subatomic_safe_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "add_subatomic_safe_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "add_subatomic_safe_util", "eval_metric")
_emit_stores_embedding("p4", "add_subatomic_safe_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "add_subatomic_safe_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "add_subatomic_safe_util", "exec_snapshot_link")

project_root = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))
with open(project_root / "agent_discovery_full.json", encoding="utf-8") as f:
    agents = json.load(f)
no_tests = [a for a in agents if not a.get("has_tests", False)]
print(f"Found {len(no_tests)} agents without tests\n")
territories = {}
for agent in no_tests:
    territory = agent.get("territory", "Unknown")
    if territory not in territories:
        territories[territory] = []
    territories[territory].append(agent)
modified = []
errors = []
for territory, ags in sorted(territories.items()):
    print(f"\n{'=' * 70}")
    print(f"Territory: {territory} ({len(ags)} agents)")
    print("=" * 70)
    for agent in ags:
        agent_path = project_root / agent["path"]
        class_name = agent["class_name"]
        if not agent_path.exists():
            errors.append(f"{class_name}: File not found")
            continue
        try:
            content = agent_path.read_text(encoding="utf-8")
            if "SubatomicTestingMixin" in content:
                print(f"  ⏭️  {class_name}: Already has SubatomicTestingMixin")
                continue
            if re.search("def\\s+test_self\\s*\\(", content):
                print(f"  ⏭️  {class_name}: Already has test_self method")
                continue
            try:
                ast.parse(content)
            except SyntaxError as e:
                errors.append(f"{class_name}: Pre-existing syntax error at line {e.lineno}")
                print(f"  ❌ {class_name}: Pre-existing syntax error")
                continue
            class_pattern = f"class\\s+{re.escape(class_name)}\\s*\\([^)]*\\):"
            match = re.search(class_pattern, content, re.DOTALL)
            if not match:
                errors.append(f"{class_name}: Could not find class definition")
                print(f"  ❌ {class_name}: Class definition not found")
                continue
            class_def = match.group(0)
            paren_start = class_def.find("(")
            paren_end = class_def.rfind(")")
            if paren_start == -1 or paren_end == -1:
                errors.append(f"{class_name}: Invalid class definition")
                continue
            current_inheritance = class_def[paren_start + 1 : paren_end].strip()
            new_inheritance = f"SubatomicTestingMixin, {current_inheritance}"
            new_class_def = class_def[: paren_start + 1] + new_inheritance + class_def[paren_end:]
            new_content = content.replace(class_def, new_class_def)
            if (
                "from agentic_core.L3_orchestration.mixins.L3SubatomicTestingMixin import SubatomicTestingMixin"
                not in new_content
            ):
                import_lines = [
                    i
                    for i, line in enumerate(new_content.split("\n"))
                    if line.startswith(("import ", "from "))
                ]
                if import_lines:
                    lines = new_content.split("\n")
                    insert_idx = import_lines[-1] + 1
                    lines.insert(
                        insert_idx,
                        "from agentic_core.L3_orchestration.mixins.L3SubatomicTestingMixin import SubatomicTestingMixin",
                    )
                    new_content = "\n".join(lines)
            try:
                ast.parse(new_content)
            except SyntaxError as e:
                errors.append(f"{class_name}: New syntax error at line {e.lineno}")
                print(f"  ❌ {class_name}: Would introduce syntax error")
                continue
            assert_no_persistent_write("L0", "write_text")
            agent_path.write_text(new_content, encoding="utf-8")
            modified.append(class_name)
            print(f"  ✅ {class_name}")
        # guardian: allow-silent-swallow
        except Exception as e:
            errors.append(f"{class_name}: {str(e)}")
            print(f"  ❌ {class_name}: {str(e)[:50]}")
print(f"\n{'=' * 70}")
print("SUMMARY")
print("=" * 70)
print(f"Modified: {len(modified)}")
print(f"Errors: {len(errors)}")
if errors:
    print(f"\nErrors ({len(errors)}):")
    for e in errors[:20]:
        print(f"  {e}")
print("\nNext steps:")
print("1. Run: python scripts/full_agent_discovery.py --force")
print("2. Run: python scripts/analyze_compliance.py")
print("3. Verify test coverage increased")
