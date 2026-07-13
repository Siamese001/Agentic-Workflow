---
name: artifact-management
description: Use this skill when creating plans, reports, evidence bundles, snapshots, or other durable repository artifacts and when selecting their canonical path, evidence shape, or bounded processing procedure.
metadata:
  owner: platform-team
  version: "2.0"
---

# Artifact management

Use this procedure for durable repository artifacts. The skill explains how to choose a path,
assemble evidence, and bound long-running processing. Deterministic path and structure policy remains
owned by repository gates; do not treat skill activation as enforcement.

## Workflow

1. Resolve the repository root dynamically:

   ```bash
   git rev-parse --show-toplevel
   ```

2. Classify the artifact before writing it. Read
   [artifact_type_resolver.md](artifact_type_resolver.md) when the destination is not obvious.
3. Validate the destination with
   [path_validation_checklist.md](path_validation_checklist.md). Use repository-relative paths in
   plans, scripts, and evidence.
4. Capture directly observed facts separately from derived findings and unresolved items. Read
   [evidence_standards.md](evidence_standards.md) for required sections on formal proof work.
5. Bound scans, subprocesses, and batch work. Read
   [bounded_operations_guide.md](bounded_operations_guide.md) before processing a directory or a
   large artifact set.
6. Use [progress_display_protocol.md](progress_display_protocol.md) only for operations whose runtime
   warrants user-visible progress. Do not duplicate terminal progress output inside persisted evidence.
7. Run the validation commands appropriate to the artifact type and inspect the resulting diff.

## Canonical destinations

| Artifact | Destination |
|---|---|
| Active execution plan | `plans/` |
| Architecture decision or design | `docs/architecture/` |
| Governance, RCA, or verification report | `docs/reports/` |
| Machine-readable evidence and generated receipts | `artifacts/` |
| Test code and fixtures | `tests/` |
| Reusable operational script | `ops_scripts/` or `tools/` according to ownership |

Do not hard-code a workstation path. Do not write active plans under `.codex/plans/`.

## Evidence rules

- Cite the command, file, or raw artifact that supports each directly observed claim.
- Name the deriving command or algorithm for computed findings.
- List unresolved facts explicitly instead of silently converting them into assumptions.
- Keep ANSI control sequences and transient progress output out of persisted evidence.
- Use one canonical evidence artifact per phase unless the artifact contract requires a bundle.

## Validation

```bash
python ops_scripts/ci/check_structure_policy.py
python ops_scripts/ci/run_skill_contract_gates.py
```

For a formal phase report, also run the domain-specific proof or test command named in the plan.

## Boundaries

- Always-on subprocess, plan-location, and structure rules belong in `AGENTS.md`, `.codex/rules/`,
  hooks, and CI.
- Use `operational-gates` for destructive or rollback-sensitive execution.
- Use `testing-framework` for test evidence and collection/execution integrity.
