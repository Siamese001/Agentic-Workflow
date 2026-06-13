# Merge Checklist — Consolidation & Governance Hardening

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Reproduce CI Locally

Copy-paste the full block below from the repo root:

```bash
export PYTHONPATH="$(pwd)"

# Phase 1: SSOT + unit tests + governance coverage
python ops_scripts/ci/manifest_ssot_check.py
python ops_scripts/ci/active_set_ssot_check.py
python -m pytest tests/core/test_active_set_ssot_check.py -q
python ops_scripts/ci/governance_coverage_check.py

# Phase 2: Active-set gates
python ops_scripts/ci/agent_count_cap.py
python ops_scripts/ci/discovery_registry_consistency_check.py
python ops_scripts/ci/active_set_snapshot_check.py

# Phase 3: MRO + remaining gates
python ops_scripts/ci/mro_new_diamond_check.py
python ops_scripts/ci/mro_contract_check.py
python ops_scripts/ci/init_contract_check.py
python ops_scripts/ci/skip_quarantine_check.py
python ops_scripts/ci/centrality_gate.py
python ops_scripts/ci/gate_consistency_check.py

# Phase 4: Full test suite
python -m pytest -q
```

Every gate must exit 0. `python -m pytest -q` must report **77 passed, 0 failed, 0 skipped**.

## Locked Values

These values must match the gate outputs above. Any mismatch indicates drift.

| Metric | Locked Value |
|--------|-------------|
| Active agent count | 149 |
| Active set fingerprint | `a3d39ecce65c6dbb0abe6f164b6323fc471dff01bb0c7d049fa100ba2f6b62c3` |
| MRO diamonds | 82 (ceiling = 82) |
| New MRO diamonds | 0 |
| pytest | 77 passed, 0 failed, 0 skipped |

## Pre-Merge Verification (Reviewer)

- [ ] Run the "Reproduce CI locally" block above — all gates exit 0
- [ ] Confirm gate outputs match every row in "Locked Values"
- [ ] Verify CI guard: `CI=true python -c "from ops_scripts.ci.baseline_io import write_json_atomic; write_json_atomic('x.json', {})"` must raise `CIWriteBlockedError`
- [ ] Spot-check `artifacts/consolidation/active_set_snapshot.json` — count=149, fingerprint matches above
- [ ] Spot-check `artifacts/consolidation/mro_diamond_baseline.json` — total=82, len(entries)=82
- [ ] Review `.github/workflows/agent-sprawl-check.yml` — phase ordering: Phase 1 → Phase 2 → Phase 3 → Phase 4

## Bump / Regenerate Protocols

### MRO Ceiling Bump (increase)

When new MRO diamonds are intentionally introduced and the ceiling must increase:

```bash
# 1. Edit artifacts/consolidation/mro_diamond_baseline.json — set "total" and add entries
# 2. Commit with tag:
git commit -m "MRO_BASELINE_BUMP:added XyzAgent diamond"
# 3. Verify:
PYTHONPATH=. python ops_scripts/ci/mro_contract_check.py
PYTHONPATH=. python ops_scripts/ci/mro_new_diamond_check.py
```

### MRO Ceiling Lower (local-only auto-lower)

When MRO diamonds are resolved and the ceiling should decrease:

```bash
# LOCAL ONLY — hard-blocked in CI
PYTHONPATH=. AUTO_LOWER_MRO_BASELINE=1 python ops_scripts/ci/mro_contract_check.py
git commit -m "MRO_BASELINE_LOWERED:82->78"
```

### New Diamond Baseline Bump (mro_new_diamond_check)

`mro_new_diamond_check.py` blocks ANY diamond whose `file:class` key is not in the baseline entries, even if total count <= ceiling. To add a new intentional diamond:

```bash
# 1. Edit artifacts/consolidation/mro_diamond_baseline.json:
#    - Add the new entry to "entries" array
#    - Increment "total" to match len(entries)
# 2. Commit with tag:
git commit -m "MRO_BASELINE_BUMP:added new diamond for XyzAgent"
# 3. Verify both gates pass:
PYTHONPATH=. python ops_scripts/ci/mro_new_diamond_check.py
PYTHONPATH=. python ops_scripts/ci/mro_contract_check.py
```

### Active Set Snapshot Bump

When agents are added, removed, or renamed:

```bash
# 1. Commit with tag — the gate auto-updates the snapshot JSON:
PYTHONPATH=. COMMIT_MESSAGE="ACTIVE_SET_SNAPSHOT_BUMP:added FooAgent" python ops_scripts/ci/active_set_snapshot_check.py
# 2. Commit the updated artifacts/consolidation/active_set_snapshot.json
```

### Centrality Baseline Bump

When a module's import count exceeds its ceiling:

```bash
# 1. Edit artifacts/consolidation/centrality_baseline.json — raise the ceiling
# 2. Commit with tag:
git commit -m "CENTRALITY_BASELINE_BUMP:SovereignBaseAgent ceiling 200->220"
# 3. Verify:
PYTHONPATH=. python ops_scripts/ci/centrality_gate.py
```

### Skip/Quarantine Ceiling Bump

When new tests are quarantined or skip count increases:

```bash
# 1. Edit tests/_quarantine/QUARANTINE_MANIFEST.json — add entry with reason + owner
# 2. Commit with tag:
git commit -m "QUARANTINE_CEILING_BUMP:quarantined test_xyz fixture issue"
# 3. Verify:
PYTHONPATH=. python ops_scripts/ci/skip_quarantine_check.py
```

## Post-Merge

- [ ] Verify CI workflow passes on `main` after merge
- [ ] If any baseline needs updating, follow the exact protocols above

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

