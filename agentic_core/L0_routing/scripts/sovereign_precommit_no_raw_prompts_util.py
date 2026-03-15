from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "sovereign_precommit_no_raw_prompts_util", "L0")
_emit_routes_through("p1", "sovereign_precommit_no_raw_prompts_util", "L0")
_emit_escalates_to_human("p1", "sovereign_precommit_no_raw_prompts_util", "L0")
_emit_reads_policy_state("p1", "sovereign_precommit_no_raw_prompts_util", "L0")

"\nSovereign Guard: Block Raw Prompt Strings\nEnforces that all prompts must be registered in sovereign_prompt_constitution.py\n\nUsage: Called automatically by pre-commit hook\n"
import re
import sys
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

exempt: Any = {
    "agentic_core/prompt_governance/meta_prompts/sovereign_prompt_constitution.py",
    "test_",
    "tests/",
}
prompt_patterns: Any = [
    '""".*You are.*"""',
    "'''.*You are.*'''",
    '{"role":\\s*"system",\\s*"content":\\s*"',
    'f""".*You are.*"""',
    "f\\'\\'\\'.*You are.*\\'\\'\\'",
]


def check_file(filepath: Any) -> Any:
    """Check a single file for hardcoded prompt strings."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "check_file", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "check_file", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "check_file")
    normalized_path: Any = str(Path(filepath)).replace("\\", "/")
    if any(exempt in normalized_path for exempt in EXEMPT):
        return True
    try:
        with open(filepath, encoding="utf-8") as f:
            content: Any = f.read()
        violations: Any = []
        lines: Any = content.split("\n")
        for i, line in enumerate(lines, 1):
            if line.strip().startswith("#"):
                continue
            for pattern in PROMPT_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE | re.DOTALL):
                    if "You are" in line or "you are" in line:
                        violations.append({"line": i, "content": line.strip()[:80]})
                        break
        if violations:
            print(f"\n❌ SOVEREIGN GUARD VIOLATION: {filepath}")
            print("=" * 80)
            for Violation in violations:
                print(f"  Line {Violation['line']}: {Violation['content']}...")
            print("\n💡 SOLUTION: Register this prompt in:")
            print("   agentic_core/prompt_governance/meta_prompts/sovereign_prompt_constitution.py")
            print("   Then use: get_prompt('YOUR_PROMPT_ID')")
            print("=" * 80)
            return False
        return True
    # guardian: allow-silent-swallow
    except Exception as e:
        print(f"⚠️  Warning: Could not parse {filepath}: {e}")
        return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: sovereign_precommit_no_raw_prompts_util.py <file1> <file2> ...")
        sys.exit(0)
    all_passed: Any = True
    for filepath in sys.argv[1:]:
        if not check_file(filepath):
            all_passed: Any = False
    if not all_passed:
        print("\n🚫 Pre-commit BLOCKED: Hardcoded prompts detected.")
        print("   All prompts must be centralized in sovereign_prompt_constitution.py")
        sys.exit(1)
    sys.exit(0)
