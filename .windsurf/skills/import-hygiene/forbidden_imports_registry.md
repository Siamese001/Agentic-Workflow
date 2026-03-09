# Forbidden Imports Registry

Authoritative list of import patterns that are FORBIDDEN in this repository.
Attempting to add any of these = CONSTITUTIONAL VIOLATION.

Last updated: 2026-03-09

---

## Category 1 — Relocated Modules (Use Canonical Path)

| Forbidden | Canonical Replacement | RCA Reference |
|---|---|---|
| `from agentic_core.base_agents.timeout_decorator import timeout` | `from agentic_core.L0_routing.utils.timeout_decorator import timeout` | `RCA_timeout_decorator_fix.md` |
| `from agentic_core.base_agents.timeout_decorator import *` | Explicit imports from canonical path | `RCA_timeout_decorator_fix.md` |

---

## Category 2 — SSOT Violations (Use Constants File)

| Forbidden | Canonical Replacement | Reason |
|---|---|---|
| `from agentic_core.L5_safety.config.structure_blueprint.ssot import *` | Import specific constants from `structure_blueprint_config.py` | Wildcard bypasses explicit dependency tracking |
| Hardcoded string `"docs/reports/plans"` in source code | `from agentic_core.L5_safety.config.structure_blueprint_config import DOCS_REPORTS_PLANS` | SSOT constant exists |
| Hardcoded string `"data/freeze_reports"` in source code | Import `FREEZE_REPORTS_DIR` constant | SSOT constant exists |
| Hardcoded string `"system_learning"` in source code | Import `SYSTEM_LEARNING_DIR` constant | `REPLACE_violations_remediation` |
| Hardcoded string `"tools"` as top-level path in source code | Import `TOOLS_DIR` constant | `REPLACE_violations_remediation` |

---

## Category 3 — Pattern Violations

| Forbidden Pattern | Reason | Allowed Alternative |
|---|---|---|
| `import *` (wildcard) in any production `.py` file | Hides dependencies, breaks static analysis | Explicit named imports |
| `import X` inside a function body for structural/config/registry logic | Module-level execution on every call, untestable | Module-level import |
| `from __future__ import annotations` without Python 3.10+ compatibility note | Can break runtime type checking | Document why if used |
| Circular imports (A imports B, B imports A) | Breaks import resolution | Restructure to remove cycle |

---

## Category 4 — Horizontal Boundary Violations

| Forbidden | Reason |
|---|---|
| `apps_rg` importing from `apps_lic` | Horizontal boundary violation |
| `apps_lic` importing from `apps_rg` | Horizontal boundary violation |
| `apps_shared` importing from `apps_rg` or `apps_lic` | Reverse dependency violation |

---

## Category 5 — Test Isolation Violations

| Forbidden | Reason | Allowed Alternative |
|---|---|---|
| Production code importing from `tests/` | Tests must not be reverse-imported | Extract shared fixtures to `apps_shared` or `agentic_core` |
| Test files importing from `ops_scripts/` directly | Ops scripts are not test infrastructure | Mock or stub the behavior |

---

## How to Update This Registry

When a new forbidden import is discovered:
1. Add to the appropriate category with: forbidden pattern, canonical replacement, reason
2. Reference the RCA or plan that identified the violation
3. Update `pre_import_checklist.md` Point 4 table if it's a common pattern
4. Add a CI check in `ops_scripts/ci/` to scan for the new pattern
