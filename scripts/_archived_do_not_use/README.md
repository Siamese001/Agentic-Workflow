# ARCHIVED — DO NOT USE

This folder contains scripts that have been **permanently banned** from the Agentic-Workflow codebase.

## Why These Scripts Are Banned

These scripts created **ghost files** — empty or stub `.py` files that existed only to satisfy a broken "100% YAML coverage" metric.

Ghost files are **anti-subatomic**:
- They make the repo lie about its capabilities
- They inflate file counts without adding value
- They create maintenance burden
- They violate the principle: "A file exists only if it does real work"

## Banned Scripts

| Script | Reason |
|--------|--------|
| `generate_scaffold.py.BANNED` | Created empty stub files to match YAML paths |

## The Law

From `unified_structure_subatomic_meta.yaml` Section 13:

```yaml
ghost_file_policy:
  rule: "A path declared in the YAML SSoT MUST contain real, executable logic."
  empty_stub_files: banned_forever
  scaffold_artifacts: banned_forever
  compliance_metric_100_percent_coverage: abolished
```

## Never Again

If you need to add a new module:
1. Write the real code first
2. Then add the path to the YAML
3. Never create empty files to "satisfy" the YAML

The YAML follows the code. The code does not follow the YAML.
