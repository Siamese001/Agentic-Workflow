"""
Phase 7: Sovereign Compliance Audit

Runs CodeValidatorAgent and StructureEnforcerAgent across the policy_engine
directory to verify sovereign namespace compliance.
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

emit_replay_key("p0", "run_sovereign_compliance_audit_util")
emit_determinism_digest("p0", "run_sovereign_compliance_audit_util")

_emit_dispatches_healing_run("p1", "run_sovereign_compliance_audit_util", "L0")
_emit_routes_through("p1", "run_sovereign_compliance_audit_util", "L0")
_emit_escalates_to_human("p1", "run_sovereign_compliance_audit_util", "L0")
_emit_reads_policy_state("p1", "run_sovereign_compliance_audit_util", "L0")

project_root = Path(__file__).resolve().parents[3]
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))
from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.L0_routing.seams.safety_reasoning_seam import load_structure_enforcer_agent
from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_code_validator
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def run_code_validator():
    """Run CodeValidatorAgent on policy_engine directory."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "run_code_validator", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "run_code_validator", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "run_code_validator")
    print("=" * 80)
    print("SOVEREIGN COMPLIANCE AUDIT: CodeValidatorAgent")
    print("=" * 80)
    policy_engine_dir = "agentic_core/L5_safety/policy_engine"
    result = invoke_code_validator(
        action="validate_directory", project_root=project_root, directory=policy_engine_dir
    )
    if result.get("success"):
        print("\nResults:")
        print(f"  Violations Found: {result.get('total_violations', 0)}")
        print(f"  Directory: {result.get('directory', policy_engine_dir)}")
    else:
        print(f"\nError: {result.get('error')}")
    return result


def run_structure_enforcer():
    """Run StructureEnforcerAgent on policy_engine directory."""
    print("\n" + "=" * 80)
    print("SOVEREIGN COMPLIANCE AUDIT: StructureEnforcerAgent")
    print("=" * 80)
    StructureEnforcerAgent = load_structure_enforcer_agent()
    enforcer = StructureEnforcerAgent()
    policy_engine_dir = project_root / AGENTIC_CORE_DIR / "L5_safety" / "policy_engine"
    result = enforcer.heal_repository(policy_engine_dir)
    print("\nResults:")
    print(f"  Violations Found: {result.get('violations_found', 0)}")
    print(f"  Violations Fixed: {result.get('violations_fixed', 0)}")
    print(f"  Status: {result.get('status', 'UNKNOWN')}")
    print(f"  Execution Time: {result.get('execution_time_ms', 0):.2f}ms")
    if result.get("error_message"):
        print(f"  Error: {result['error_message']}")
    return result


def main():
    """Run sovereign compliance audit."""
    print("\n" + "=" * 80)
    print("PHASE 7: SOVEREIGN COMPLIANCE AUDIT")
    print("=" * 80)
    print(f"Target: {project_root / AGENTIC_CORE_DIR / 'L5_safety' / 'policy_engine'}")
    print()
    code_result = run_code_validator()
    structure_result = run_structure_enforcer()
    print("\n" + "=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)
    total_violations = code_result.get("violations_found", 0) + structure_result.get("violations_found", 0)
    total_fixed = code_result.get("violations_fixed", 0) + structure_result.get("violations_fixed", 0)
    print(f"Total Violations Found: {total_violations}")
    print(f"Total Violations Fixed: {total_fixed}")
    code_status = code_result.get("status", "UNKNOWN")
    structure_status = structure_result.get("status", "UNKNOWN")
    if code_status == "PASS" and structure_status == "PASS":
        print("\n✅ SOVEREIGN COMPLIANCE: VERIFIED")
        return 0
    else:
        print("\n⚠️  COMPLIANCE STATUS:")
        print(f"   CodeValidator: {code_status}")
        print(f"   StructureEnforcer: {structure_status}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
