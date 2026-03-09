# Scope Pre-Check

Run BEFORE any edits. Failure to complete this block → phase MUST NOT proceed.

## Step 1 — Build Dependency Graph (§3.4 MANDATORY)

**BEFORE declaring scope, build AST dependency graph to determine true impact.**

Required analysis:
- Module import edges
- Symbol import edges
- Class inheritance edges
- Function/method call edges
- Registry/factory resolution edges
- Test coverage edges

**Output:**
```
DEPENDENCY_GRAPH (pre-scope):
Proposed changes: [list initial files]
Graph analysis reveals:
  - Direct dependencies: [list]
  - Downstream dependents: [list]
  - Required test files: [list]
  - Cross-layer implications: [list]

True scope (graph-derived): [final file list]
```

**FORBIDDEN (§3.5):**
- ❌ Using grep to determine scope
- ❌ Filename similarity guessing
- ❌ Text search for impact analysis

## Step 2 — Declare Planned File List

List every file that will be modified/created. No wildcards.

**Each file MUST be justified by dependency graph (§3.7).**

```
Declared scope (N = _):
1. path/to/file1.py   [intent: replace lines X-Y]
   Graph justification: Direct modification target

2. path/to/file2.py   [intent: add function Z]
   Graph justification: Downstream dependent (import edge from file1.py)

3. tests/test_file1.py   [intent: add tests]
   Graph justification: Test coverage edge required per §5.2
...
```

**Any file without graph justification = scope contamination.**

## Step 3 — Capture Pre-Change Diff

```powershell
$E = "docs/reports/plans/<phase_evidence_file>.md"
git diff --name-only HEAD 2>&1 | Tee-Object -FilePath $E -Append
```

Record the output. This is the baseline dirty-file set (pre-existing, not this phase).

## Step 4 — Verify N After Edits

After edits, run:

```powershell
git diff --name-only HEAD 2>&1 | Tee-Object -FilePath $E -Append
```

Compare to declared scope:
- New files in diff that are NOT in declared scope → STOP immediately.
- **Verify each file has graph justification (§3.7)**
- Execute Decontamination Protocol (`decontamination_protocol.md`).
- Do NOT commit until scope matches declaration.

**Graph-backed verification:**
```
For each file in diff:
  - Check: Is file in declared scope? YES/NO
  - Check: Does file have graph justification? YES/NO
  - If NO to either → SCOPE CONTAMINATION
```

## STOP Conditions

| Condition | Action |
|-----------|--------|
| Modified files exceed N | STOP → Decontaminate → Revise plan |
| File outside declared scope appears | STOP → Decontaminate |
| Unrelated pre-existing file staged | STOP → Unstage → Document |
