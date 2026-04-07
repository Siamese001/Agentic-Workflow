# CI Promotion Authority — W4.5

**Document type:** Governance policy  
**Scope:** Code promotion from local → CI → main  
**Owner:** SVP Engineering persona (Constitutional §9)  
**Created:** Wave 4, Phase 4.5

---

## Promotion Tiers

| Tier | Stage | Gate Requirements | Approver |
|------|-------|-------------------|----------|
| **T-Local** | Developer workstation | All `pre-commit` hooks green (T0–T21) | None (automated) |
| **T-PR** | Pull Request | GitHub Actions CI suite green, no `cmd /c` regressions | Peer review |
| **T-Main** | `main` branch | All CI gates green + promotion criteria below | Auto-merge if all pass |
| **T-Release** | Tagged release | Full suite + manual smoke test + ADG health check | Release owner |

---

## Promotion Criteria (main ← PR)

All of the following MUST be green before merging to `main`:

### Hard Gates (block merge if failing)
1. **Pre-commit passes** — all T0–T21 hooks exit 0 on `--no-verify`-free commit
2. **Ruff lint P0+P1** — zero blocking severity violations (`ruff_severity_gate.py`)
3. **ADG unified gate** — no `ADG:CRITICAL` layer violations (`adg_unified_gate.py`)
4. **Guardian exemption ratchet** — exemption count ≤ baseline (`guardian_exemption_gate.py`)
5. **No archives imports** — zero `from archives.` in production code (`check_no_archives_imports.py`)
6. **No secrets leaked** — secrets scan clean (`check_secrets_scan.py`)
7. **Hollow file gate** — no new hollow files after refactor (`hollow_file_gate.py`)
8. **PowerShell ban** — zero `subprocess` calls using `powershell`/`pwsh` (`check_powershell_ban.py`)

### Advisory Checks (warn, do not block)
- Ruff lint P2+P3 warnings surfaced in PR comment
- ADG:HIGH suggest-fix report attached to PR
- Guardian quality scanner report (weak justification count)
- Memory health check (entity count, staleness)

---

## High-Risk Change Path

A change is **high-risk** if it touches any of:
- `agentic_core/` — production routing/orchestration
- `ops_scripts/ci/` — CI gate scripts (self-modifying enforcement)
- `.pre-commit-config.yaml` — gate configuration
- `mcp_config.json` — MCP server configuration
- `tools/generate/` — ADG generator

**High-risk promotion requires:**
1. All hard gates above pass
2. ADG regenerated after change (`python tools/generate_full_adg.py`)
3. Scoped test suite passes (`pytest tests/unit -q`)
4. HITL approval documented in PR description

---

## Approval Classes

| Class | Trigger | Required Action |
|-------|---------|-----------------|
| **AUTO** | All hard gates pass, no high-risk files | Auto-merge allowed |
| **PEER_REVIEW** | High-risk files touched OR any advisory warning | One reviewer approval required |
| **HITL_REQUIRED** | New guardian exemption OR anti-pattern introduction | HITL decision record in PR |
| **BLOCKED** | Any hard gate fails | Fix gates before re-submitting |

---

## Escalation Path

```
Developer → pre-commit local (T-Local)
         → Push → PR CI (T-PR)
         → All gates green? → Auto or peer-merge (T-Main)
         → Tagged? → Release owner smoke test (T-Release)
```

**Escalation on block:**
1. Identify failing gate from CI output
2. Classify: `production_bug_fix` | `stale_reference_fix` | `broken_test_fix` | `policy_regression_fix`
3. Fix root cause (not call sites — see ADG repair discipline §ADG-1.3)
4. Re-run scoped tests only until green
5. Re-submit PR

---

## Risk Classes

| Risk Class | Definition | Examples |
|------------|------------|---------|
| **CRITICAL** | Hard gate fails, blocks production | ADG:CRITICAL violation, secrets leak, broken import |
| **HIGH** | Advisory warning, degrades quality | ADG:HIGH defect, guardian weak justification |
| **MEDIUM** | Style/format drift | Ruff P2 violations, whitespace |
| **LOW** | Documentation, comment changes | Docstring updates, plan files |

---

## Exception Process

Bypass via `git commit --no-verify` is **allowed only for**:
- Fixing a broken pre-commit hook itself (bootstrapping)
- Emergency hotfix with documented post-hoc gate verification

Every `--no-verify` commit is logged by `guard_no_verify.py` and must include
a justification in the commit message or a follow-up gate verification commit
within 24 hours.
