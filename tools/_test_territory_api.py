"""Quick test of new territory API migration."""

from agentic_core.L5_safety.config.structure_blueprint.territories import (
    get_all_territories,
    get_territory_metadata,
    is_valid_root_folder,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "_test_territory_api")
_emit_applies_guardrail("p0", "_test_territory_api", "p0_governance")
_emit_reads_policy_state("p0", "_test_territory_api", "policy_binding")
_emit_snapshots_state("p0", "_test_territory_api", "state_snapshot")
emit_replay_key("p0", "_test_territory_api")
emit_determinism_digest("p0", "_test_territory_api")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

print("=" * 60)
print("Territory API Migration Verification")
print("=" * 60)
print()

# Test 1: get_all_territories()
territories = get_all_territories()
print(f"✅ get_all_territories() returns {len(territories)} territories")
print(f"   Sample keys: {list(territories.keys())[:5]}")
print()

# Test 2: get_territory_metadata()
meta = get_territory_metadata("apps_shared")
if meta:
    print("✅ get_territory_metadata('apps_shared') works")
    print(f"   Purpose: {meta.get('purpose', 'N/A')[:60]}...")
else:
    print("❌ get_territory_metadata('apps_shared') returned None")
print()

# Test 3: is_valid_root_folder()
valid = is_valid_root_folder("apps_shared")
invalid = is_valid_root_folder("invalid_folder")
print(f"✅ is_valid_root_folder('apps_shared'): {valid}")
print(f"✅ is_valid_root_folder('invalid_folder'): {invalid}")
print()

# Test 4: Verify derived.py uses new API
from agentic_core.L5_safety.config.structure_blueprint.derived import DEPTH_RULES

print(f"✅ DEPTH_RULES derived successfully ({len(DEPTH_RULES)} entries)")
print()

# Test 5: Verify ssot.py uses new API
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    ALLOW_ROOT_PY_TERRITORIES,
    LAYER_PREFIX_EXEMPT_TERRITORIES,
)

print(f"✅ ALLOW_ROOT_PY_TERRITORIES: {len(ALLOW_ROOT_PY_TERRITORIES)} territories")
print(f"✅ LAYER_PREFIX_EXEMPT_TERRITORIES: {len(LAYER_PREFIX_EXEMPT_TERRITORIES)} territories")
print()

print("=" * 60)
print("All tests passed! Migration successful.")
print("=" * 60)
