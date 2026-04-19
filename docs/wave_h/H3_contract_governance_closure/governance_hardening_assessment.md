# H3 — Governance Hardening Assessment

wave: H3
adg_snapshot: artifacts/adg/adg_indexed_04182026_1558.sqlite
adg_snapshot_timestamp: "04182026_1558"

## Scope

- `B7-G2b-06` (`EGRESS_GUARD_DISABLED` audit gap)
- `DISABLE_RUNTIME_MUTATION_GUARD` bypass posture

## H1 closure tests applied

### B7-G2b-06

1. egress-guard override action is auditable
2. audit fields satisfy governance minimum
3. exception workflow documented with owner accountability

### DISABLE_RUNTIME_MUTATION_GUARD

1. bypass path policy-constrained
2. bypass events auditable
3. unauthorized bypass attempts fail by policy

## Evidence quality classification

### Existing evidence of control

- `agentic_core/L2_execution/enforcement/network_egress_guard.py` enforces guard path by default and blocks unauthorized direct egress unless bypass env is set.
- `agentic_core/L0_routing/enforcement/runtime_mutation_guard.py` provides mutation-guard enforcement path by default.
- G4b/G7 docs consistently classify both keys as critical control-plane risk surfaces and open production blockers.

### Narrative-only control

- `docs/wave_g/G4b_control_plane/kill_switches_and_risk.md` recommends change-control discipline and non-prod restrictions but does not provide enforceable audit contract evidence.
- owner/accountability assignment exists at matrix level (`docs/wave_h/H1_blocker_reduction/owner_matrix.md`) but is not backed by an auditable exception workflow artifact.

### Missing control

- No direct evidence of structured audit event records for `EGRESS_GUARD_DISABLED` activation with governance-minimum fields.
- No direct evidence of policy gate requiring authorized context before setting `DISABLE_RUNTIME_MUTATION_GUARD`.
- No direct evidence that unauthorized bypass attempts fail by policy (bypass appears to succeed if env is set).

## H3 closure-test outcomes

### B7-G2b-06

- Test 1: **fail** (only warning log path seen; no structured audit evidence bundle)
- Test 2: **fail** (no governance-minimum audit fields evidenced)
- Test 3: **partial** (owners identified, but exception workflow remains narrative)

Result: **open; narrowed to explicit missing-audit artifact set**.

### DISABLE_RUNTIME_MUTATION_GUARD

- Test 1: **fail** (env-based bypass not policy-constrained in observed code path)
- Test 2: **fail** (no structured bypass-audit evidence)
- Test 3: **fail** (no evidence unauthorized bypass attempts are policy-rejected)

Result: **open; control remains trust-based rather than governed/auditable**.
