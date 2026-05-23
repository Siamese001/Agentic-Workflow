# Exec v2 Mermaid sources

Diagrams use **short node labels**, 10px font, and tight spacing for readable SVG preview. Detail lives in the v2 markdown tables and ASCII SSOT.

Sources for [`agentic_system_process_map_exec_v2.md`](../agentic_system_process_map_exec_v2.md).

## Re-render all SVGs (from this directory)

```bash
mkdir -p rendered
for f in *.mmd; do
  npx @mermaid-js/mermaid-cli -i "$f" -o "rendered/${f%.mmd}.svg" -b transparent
done
```

PowerShell:

```powershell
New-Item -ItemType Directory -Force rendered | Out-Null
Get-ChildItem *.mmd | ForEach-Object {
  npx @mermaid-js/mermaid-cli -i $_.Name -o "rendered\$($_.BaseName).svg" -b transparent
}
```

## Files

| Source | Rendered |
|--------|----------|
| `01-cross-cutting-planes.mmd` | `rendered/01-cross-cutting-planes.svg` |
| `02-runtime-spine.mmd` | `rendered/02-runtime-spine.svg` |
| `03-l0-routing.mmd` | `rendered/03-l0-routing.svg` |
| `04-l2-execute.mmd` | `rendered/04-l2-execute.svg` |
| `05-exit-x3.mmd` | `rendered/05-exit-x3.svg` |
