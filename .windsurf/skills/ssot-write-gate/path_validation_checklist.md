# Path Validation Checklist

Run BEFORE writing any artifact file to disk.
ALL checks must pass. Any FAIL = do not write, resolve path first.

---

## Step 1 — Repository Root Check

```
Target path: <full_absolute_path>

Is the path under c:\Git\Agentic-Workflow\ ?
  YES → proceed to Step 2
  NO  → FAIL — path is outside repository
         Remap to SSOT location using artifact_type_resolver.md
```

Paths that auto-FAIL Step 1:
- `C:\Users\<username>\...` — user home directory
- `C:\Users\<username>\.windsurf\plans\...` — user IDE directory
- Any absolute path NOT starting with `c:\Git\Agentic-Workflow\`

---

## Step 2 — PROJECT_ROOT_WHITELIST Check

Extract the first path component after the repository root:

```
c:\Git\Agentic-Workflow\<FIRST_COMPONENT>\...
```

Approved first components (PROJECT_ROOT_WHITELIST):

| Component | Approved | Notes |
|---|---|---|
| `agentic_core` | ✅ | Core library |
| `apps_rg` | ✅ | Resume generator app |
| `apps_lic` | ✅ | LIC app |
| `apps_shared` | ✅ | Shared app utilities |
| `ops_scripts` | ✅ | CI and operational scripts |
| `tests` | ✅ | Test suite |
| `docs` | ✅ | Documentation and reports |
| `data` | ✅ | Data files |
| `tools` | ✅ | Developer tools |
| `artifacts` | ✅ | Generated artifacts |
| `system_learning` | ✅ | Learning pipeline |
| `.git` | ✅ | Git internals only |
| `.github` | ✅ | CI workflows only |
| `.windsurf` | ⚠️ | IDE config ONLY — never project artifacts |
| `.backup` | ✅ | Backups only |
| Anything else | ❌ | FAIL — not in whitelist |

---

## Step 3 — Artifact Type Check

Use `artifact_type_resolver.md` to confirm the target path matches the artifact type:

```
Artifact type: <plan / evidence / report / test / source / constant / data>
Expected path: <from resolver>
Actual target: <your target path>

Match? YES → PASS
       NO  → FAIL — remap to expected path
```

---

## Step 4 — IDE System Path Check

Reject writes to IDE system directories for project artifacts:

| Path Pattern | Verdict |
|---|---|
| `.windsurf/plans/` | ✅ APPROVED for plans, evidence, RCAs |
| `.windsurf/skills/` | ✅ Only for skill SKILL.md and supporting files |
| `.windsurf/workflows/` | ✅ Only for workflow .md files |
| `.windsurf/rules/` | ✅ Only for .windsurfrules |
| `.vscode/` | ⚠️ IDE settings only — never project artifacts |
| `.cursor/` | ⚠️ IDE settings only — never project artifacts |

---

## Validation Summary

```
PATH VALIDATION:
  Target: <path>
  Step 1 (repo root):   PASS / FAIL
  Step 2 (whitelist):   PASS / FAIL — component: <first_component>
  Step 3 (type match):  PASS / FAIL — expected: <canonical_path>
  Step 4 (IDE check):   PASS / FAIL
  OVERALL:              APPROVED / BLOCKED
```

Write ONLY if OVERALL = APPROVED.
