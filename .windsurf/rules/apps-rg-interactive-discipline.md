---
trigger: always_on
description: Apply when invoking `python -m apps_rg` or discussing target-company/role/JD/briefing. Enforces Cascade discipline complementing the in-app wizard and cross-company guard.
---

# apps_rg Interactive Discipline — Cascade Must Not Auto-Fill Mandatory Inputs

> ⛔ Cascade MUST NOT pre-fill `--target-company`, `--target-role`, `--jd`, or `--manual-brief` from inferred context. The in-app wizard owns these decisions.

Sibling to `scope-containment.md`. This rule prevents Cascade from substituting pattern-matches for explicit user decisions on target company.

## Why this rule exists

`apps_rg` generates resumes. Three inputs determine the target:

| Input | Flag | Example |
|---|---|---|
| Company | `--target-company` | "Brown & Brown" |
| JD | `--target-role` + `--jd` | Title + full description |
| Briefing | `--manual-brief` or `--auto-research-tavily` | Path or research delegation |

Auto-filling from prior turns, filenames, or `apps_rg/scripts/` artifacts risks targeting the *wrong company* — a cross-company contamination defect. The repo history of 60+ stale `generated_resume_*.json` files demonstrates this risk.

The in-app fix: `_interactive_wizard(args)` prompts for the 3 items when stdin is a TTY, writing to `_interactive_*.json` files (validated by the contamination guard). This rule is the behavioral complement: prevent pre-filling flags before the wizard runs.

## Hard rules

### 1. Default invocation is verbatim

When the user types `python -m apps_rg` (or "run apps_rg", "generate a resume with apps_rg", etc.) without explicitly naming a company/role/JD in the SAME turn:

- Cascade MUST run the command exactly as typed.
- Cascade MUST NOT add `--target-company`, `--target-role`, `--jd`, or `--manual-brief` flags.
- The in-app wizard will prompt the user for the 3 mandatory inputs.

### 2. Cascade MAY surface available context

Cascade MAY list files in `apps_rg/scripts/` as informational context (e.g. "wizard will prompt; `jd_brown_brown_*.json` available"). This does NOT pre-fill flags.

### 3. Explicit in-turn authorization only

Cascade MAY auto-fill ONLY when the user, in the SAME turn, names company + role:

| User says | Cascade MAY |
|---|---|
| "Run apps_rg for Brown & Brown SVP IT Strategy" | Add `--target-company "Brown & Brown" --target-role "SVP IT Strategy"`. JD/briefing via wizard unless user names file path. |
| "Run apps_rg" (no company/role) | ❌ MUST NOT infer from prior turns |
| "Run apps_rg again" | ❌ MUST NOT reuse from session memory |

### 4. Stale-file scan forbidden as flag source

Cascade MUST NOT scan `apps_rg/scripts/` for `jd_*.json`, `company_research*.json`, etc. to auto-fill `--jd` or `--manual-brief`. Use wizard's `@path/to/file` syntax only.

### 5. Non-TTY contexts differ

In CI/batch runs, the wizard does NOT fire — `parser.error()` hard-fails on missing flags. Operators MUST supply flags explicitly. This rule applies to Cascade-mediated interactive sessions only.

## Forbidden patterns

| Pattern | Status |
|---|---|
| Auto-fill `--target-company`/`--target-role` from filename when user didn't name them | ❌ |
| Read `jd_*.json` to extract title for `--target-role` | ❌ |
| Read `company_research.json` `company` field for `--target-company` | ❌ |
| Reuse `target-company` from prior conversation context | ❌ |
| "Helpfully" run with most recent JD while user still framing intent | ❌ |

## Defense-in-depth layers

| Layer | Mechanism | Location |
|:---:|:---|:---|
| 1 | TTY-only `_interactive_wizard()` prompts for 3 inputs | `apps_rg/__main__.py` |
| 2 | `_assert_artifact_matches_company()` raises on mismatch | `apps_rg/__main__.py` |
| 3 | Cross-company contamination tests | `tests/_apps_contract/` |
| 4 | **This rule** — Cascade does not pre-fill flags | `.windsurf/rules/` |

Layers 1–3 are runtime/test enforcement. This rule is the pre-emptive layer.

## Sibling apps

Extend rule scope when sibling apps adopt wizard patterns for target/scope inputs. Current scope: `apps_rg` only (only app with wizard as of 2026-05-06).

## Empirical incident (2026-05-06)

User: `python -m apps_rg`. Cascade auto-filled flags from prior session JD + Brown & Brown context. Cross-company guard caught mismatch (stale brief was Blend360-targeted). User RCA: "always mandatory interactive — mention what loaded but cannot auto run". Wizard added (`d613a5c18a`); this rule is the behavioral complement.

## References

- Constitutional §6, §18
- `scope-containment.md` (sibling)
- `apps_rg/__main__.py` — `_interactive_wizard`, `_assert_artifact_matches_company`
- `tests/_apps_contract/test_apps_rg_cross_company_contamination_guard.py`
