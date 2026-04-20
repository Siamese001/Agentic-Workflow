---
description: Enforce timeout and progress reporting requirements for all queries
---

> **Claude workflow note:** This workflow is a reusable procedural lane, not always-on policy. Use it to hold staged retrieval, evidence gathering, execution order, and verification steps that would otherwise overload rules. For deep research, separate retrieval, quote extraction, synthesis, and final verification into distinct phases.

# Timeout & Progress Enforcement Workflow

This workflow ensures all queries and long-running operations comply with §9 timeout and progress requirements.

## Step 1: Identify Operations Requiring Timeout/Progress

Before writing any code with queries or long-running operations:

- Identify all queries (grep, search, AST parsing, database queries)
- Identify all long-running operations (>5 seconds expected)
- Classify each operation by type (fast/medium/heavy/external)

## Step 2: Apply Timeout Requirements

For each identified operation:

```python
# Import timeout utilities
from contextlib import contextmanager
import subprocess

# Define timeout based on operation type
TIMEOUT_SECONDS = 60  # Adjust based on operation type:
# Fast queries: 5-30s
# Medium queries: 30-120s
# Heavy queries: 120-600s
# External API: 10-60s

# Apply timeout to subprocess calls
result = subprocess.run(
    cmd,
    timeout=TIMEOUT_SECONDS,
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace"
)
```

## Step 3: Apply Progress Reporting

For operations expected to take >5 seconds:

```python
from tqdm import tqdm

# Initialize progress bar with total items
with tqdm(total=len(items), desc="Operation name", unit="item") as pbar:
    for item in items:
        # Process item
        result = process_item(item)

        # Update progress
        pbar.update(1)
```

## Step 4: Combine Timeout + Progress

For comprehensive compliance:

```python
from tqdm import tqdm
import subprocess

TIMEOUT_SECONDS = 90

with tqdm(total=len(items), desc="Processing", unit="item") as pbar:
    for item in items:
        # Each operation has timeout
        result = subprocess.run(
            ["process", item],
            timeout=TIMEOUT_SECONDS,
            capture_output=True,
            text=True
        )

        pbar.update(1)
```

## Step 5: Document in Evidence

Add required sections to evidence files:

```markdown
## TIMEOUT_CONFIGURATION

- Operation: <operation_name>
- Timeout: <seconds>s
- Timeout triggered: <yes/no>
- Progress reporting: enabled
- Total items: <count>
- Completed items: <count>
- Duration: <actual_seconds>s

## PROGRESS_REPORTING

- Operation: <operation_name>
- Total items: <count>
- Completed items: <count>
- Completion: <percentage>%
- Duration: <seconds>s
- Rate: <items/sec> items/sec
```

## Step 6: Validate Compliance

Run validation checks:

```bash
python ops_scripts/ci/validate_timeout_progress.py
```

Check for violations:
- [ ] All queries have explicit timeout parameters
- [ ] No infinite loops without timeout guards
- [ ] Operations >5s have progress bars
- [ ] Progress shows percentage completion
- [ ] Evidence includes TIMEOUT_CONFIGURATION section
- [ ] Evidence includes PROGRESS_REPORTING section

## References

- Constitutional Rule: `.windsurf/rules/constitutional.md` §9
- Enforcement Skill: `.windsurf/skills/artifact-management/SKILL.md` (progress display protocol covers timeout+progress)

> **Skill directory note:** The `timeout-progress-enforcement` skill directory is not present in the current `.windsurf/skills/` layout (7 canonical skills as of 2026-04-14). References to `.windsurf/skills/timeout-progress-enforcement/` are stale and should not be used.
