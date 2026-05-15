# Bounded Operations Guide

## File Limit Defaults

| Scope | Default Limit | Configurable |
|---|---|---|
| File analysis operations | 1,000 files | Yes |
| ADG node queries | 100 nodes (per call) | Via `limit=` param |
| Redis scan results | 200 keys | Via `limit=` param |

## Required Safeguards

Every file analysis loop MUST include:

1. **Maximum file limit** — stop processing after N files
2. **Early termination condition** — stop when patterns converge before limit
3. **Batch processing** — never process all files in one unbounded loop
4. **Progress reporting** — report after each batch (see `progress_display_protocol.md`)
5. **Windows compatibility** — no Unix-only commands (`head`, `tail` without fallback)

## Early Termination Patterns

```python
MAX_FILES = 1000
processed = 0
for path in all_paths:
    if processed >= MAX_FILES:
        break
    process(path)
    processed += 1
```

## Windows Compatibility Checklist

- Use `pathlib.Path` not `os.path` string concatenation
- Use `subprocess.run(argv, shell=False, timeout=30)` — no shell=True
- Avoid `head`/`tail` — use Python slicing instead
- Use `encoding="utf-8", errors="replace"` on all file reads
