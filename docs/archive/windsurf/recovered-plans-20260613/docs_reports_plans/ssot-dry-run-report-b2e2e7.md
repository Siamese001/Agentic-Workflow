# Execute SSOT Entrypoint Dry-Run Report

Run `execute_ssot_entrypoint.py` on agentic_core in dry-run mode, capturing all agent healing proposals, violation findings, and phase results into a detailed report at `docs/reports/plans/ssot_dry_run_agentic_core.md`.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Invocation

The entrypoint requires `--legacy` flag and supports `--dry-run` for preview mode. The `--domains` flag scans 5 territories (prompt_governance, L5_safety, L3_orchestration, L2_execution, L0_maintenance) but misses L1_cognition, L4_state, L6_observability. To get full agentic_core coverage, I'll run both:

1. `--legacy --dry-run --domains -vv` — multi-domain sweep (5 territories)
2. `--legacy --dry-run --territory <layer> -vv` — for L1, L4, L6 individually

## Pipeline Phases (per territory)

The SSOT pipeline executes 5 phases per territory:
- **Phase 1**: Discovery (FilesystemSSOTReconcilerAgent, LocationAgent scan)
- **Phase 2**: Reconciliation (write/heal violations)
- **Phase 2.5**: Structural alignment (HierarchyAgent) + Sovereignty enforcement (FileClassificationAgent)
- **Phase 3**: Architectural validation (ArchitectureGovernorAgent, SystemArchitectAgent)
- **Phase 4**: Final healing (Governor-driven)
- **Phase 4.5**: Additional agents (DebateSynthesisAgent, RootHygieneAgent)
- **Phase 5**: Certification

In dry-run mode, healing actions are skipped but violations are still detected and reported.

## Steps

1. Run `--domains` sweep, capture stdout+stderr to log file
2. Run individual `--territory` for L1_cognition, L4_state, L6_observability
3. Parse all output into structured report sections:
   - Per-territory violation summary
   - Agent execution results
   - Proposed moves/renames (file diffs)
   - Phase completion status
   - Decision engine confidence breakdown
4. Write report to `docs/reports/plans/ssot_dry_run_agentic_core.md`

## Output

`docs/reports/plans/ssot_dry_run_agentic_core.md` (SSOT location per §0)

## Risk

Zero — `--dry-run` flag ensures no file mutations occur.

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

