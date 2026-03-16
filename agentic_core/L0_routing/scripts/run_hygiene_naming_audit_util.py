"""
Hygiene Guardian Naming Audit Runner
-------------------------------------
Scans the codebase for filename length violations (>5 words).
"""

import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "run_hygiene_naming_audit_util")
emit_determinism_digest("p0", "run_hygiene_naming_audit_util")

_emit_dispatches_healing_run("p1", "run_hygiene_naming_audit_util", "L0")
_emit_routes_through("p1", "run_hygiene_naming_audit_util", "L0")
_emit_escalates_to_human("p1", "run_hygiene_naming_audit_util", "L0")
_emit_reads_policy_state("p1", "run_hygiene_naming_audit_util", "L0")

root = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(root))
from agentic_core.L0_routing.seams.safety_validators_seam import load_hygiene_guardian
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def main():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "main", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "main", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "main")
    root = Path(__file__).parent.parent
    HygieneGuardianAgent = load_hygiene_guardian()
    guardian = HygieneGuardianAgent(project_root=root)
    print("=" * 80)
    print("HYGIENE GUARDIAN: FILENAME LENGTH AUDIT")
    print("=" * 80)
    print(f"Scanning: {root}")
    print("Max words allowed: 5")
    print()
    violations = guardian.audit_naming_conventions()
    if violations:
        print(f"\n{'=' * 80}")
        print(f"SUMMARY: Found {len(violations)} files exceeding word limit")
        print(f"{'=' * 80}\n")
        by_count = {}
        for v in violations:
            count = v["current_count"]
            by_count.setdefault(count, []).append(v)
        for count in sorted(by_count.keys(), reverse=True):
            viols = by_count[count]
            print(f"\n{count} WORDS ({len(viols)} files):")
            for v in viols[:10]:
                print(f"  - {v['file']}")
                print(f"    Suggested: {v['suggestion']}")
            if len(viols) > 10:
                print(f"  ... and {len(viols) - 10} more")
    else:
        print("\n✅ All filenames comply with word limit!")


if __name__ == "__main__":
    main()
