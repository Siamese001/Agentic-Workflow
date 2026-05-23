# v40 Mermaid sources

Diagrams use **short node labels**, 10px font, and tight spacing. Long substep chains are collapsed (e.g. C0 → pre/fetch/contract). Full prose: v40 SSOT + v2 tables.

Sources for [`agentic_process_mapping_v40_v2.md`](../agentic_process_mapping_v40_v2.md).

SSOT ASCII: [`agentic_process_mapping_v40.md`](../agentic_process_mapping_v40.md).

## Re-render (PowerShell, from this directory)

```powershell
New-Item -ItemType Directory -Force rendered | Out-Null
Get-ChildItem *.mmd | ForEach-Object {
  npx @mermaid-js/mermaid-cli -i $_.Name -o "rendered\$($_.BaseName).svg" -b transparent
}
```

## Diagram index

| # | Source | Topic |
|---|--------|--------|
| 01 | `01-cross-cutting-planes.mmd` | L5 + 00C |
| 02 | `02-runtime-spine-overview.mmd` | Full spine overview |
| 03 | `03-l0-route-branches.mmd` | R1A/R1B/R5/R3/R4/R3R4 |
| 04 | `04-c0-pa-grounding.mmd` | C0.0–C0.6 + PA.0–PA.7 |
| 05 | `05-l3-managed-workflow.mmd` | L3 step loop |
| 06 | `06-l2-execute-pipeline.mmd` | E1–E5 + E3 lanes |
| 07 | `07-exit-x3-uwg.mmd` | Exit substeps + X3 + UWG |
| 08 | `08-l6-post-run-learning.mmd` | L6.1–L6.7 |
| 09 | `09-u0-l1-substeps.mmd` | U0.1–U0.5 + L1.1–L1.6 |
