# Hardening Accelerators

Hardening accelerators for P0, P1, and P2 dimension wiring.

## Files

- **p0_batch_wirer.py**: P0 dimension hardening (symlink to ../../../p0_batch_wirer.py)
  - Dimensions: evidence, governance, trace, runtime
  - Micro-wave batch processing (15 modules at a time)
  - Wires emit calls per layer x dimension

- **p1_batch_wire.py**: P1 orchestration hardening (symlink to ../../../p1_batch_wire.py)
  - Routes to agent
  - Dispatches execution plan
  - Validates agent capability
  - Checks agent registry

- **p2_batch_wire.py**: P2 execution capability hardening (if exists)
  - Authorizes and executes
  - Validates capability
  - Routes to capability
  - Writes via UWG

## Usage

```bash
# Via unified CLI
python -m tools.adg.accelerators hardening p0 --layer L3 --dim evidence --apply
python -m tools.adg.accelerators hardening p1 --apply
python -m tools.adg.accelerators hardening p2 --apply

# Direct usage
python tools/p0_batch_wirer.py --layer L3 --dim evidence --apply
python tools/p1_batch_wire.py --apply
```

## Dimensions

### P0 Dimensions
- **evidence**: records_execution_trace, emits_replay_key, emits_determinism_digest
- **governance**: applies_guardrail, verifies_policy, validated_by_safety_plane
- **trace**: signs_execution_trace, snapshots_state
- **runtime**: emits_replay_key, emits_determinism_digest

### P1 Dimensions
- routes_to_agent
- orchestrates_workflow
- dispatches_execution_plan
- validates_agent_capability
- checks_agent_registry

### P2 Dimensions
- authorize_and_execute
- validates_capability
- routes_to_capability
- writes_via_uwg
- blocks_direct_write
- records_tool_invocation
- captures_execution_output

## CI Integration

CI workflow: `.github/workflows/adg-accelerators-ci.yml`
- Job: `hardening-p0-check`
- Job: `hardening-p1-check`
- Job: `hardening-p2-check`
