---
description: Triage _adg.py test files using ADG fan-in analysis.
---

> **Cursor Agent workflow note:** This workflow is a reusable procedural lane, not always-on policy. Use it to hold staged retrieval, evidence gathering, execution order, and verification steps that would otherwise overload rules. For deep research, separate retrieval, quote extraction, synthesis, and final verification into distinct phases.

# ADG Fan-In Test Triage Gate

This workflow provides a structured process for classifying `_adg.py` test files as either "stubs" or "non-stubs" using ADG fan-in analysis. It should be invoked before any `_adg.py` file is deleted or archived.

### Step 1: Classify the File

Use the `adg_test_triage.py` accelerator to classify the target file.

```bash
python tools/adg/adg_test_triage.py classify --pattern <file_path>
```

### Step 2: Analyze the Classification

Review the output of the classification script. The classification is based on the following criteria:

-   **Stub**: The file has ≤2 tests and is import-only.
-   **Non-stub**: The file has >2 tests or contains production coverage edges.

### Step 3: Make a Triage Decision

Based on the classification, decide on the appropriate action:

-   **If the file is a stub**: It is a candidate for archival. Proceed to Step 4.
-   **If the file is a non-stub**: It should be kept and maintained. The workflow is complete.

### Step 4: Authorize Archival (for stubs only)

If the file is classified as a stub, a Author-Gate gate is required to authorize its archival. Present the following options to the user:

> The file `<file_path>` has been classified as a stub. How should I proceed?
>
> **Option A**: Archive the file to `tools/archive/stub_tests/`.
> **Option B**: Keep the file.

### Step 5: Execute the Chosen Action

-   **If Option A is chosen**: Archive the file and record the action in the evidence.
-   **If Option B is chosen**: Take no action. The workflow is complete.
